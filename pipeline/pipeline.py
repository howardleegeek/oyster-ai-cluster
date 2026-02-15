#!/usr/bin/env python3
"""
Pipeline Infra CLI — 六层自动化生产流程
Usage:
  python3 pipeline.py run <project> [--layer L1] [--from L3]
  python3 pipeline.py status [<project>]
  python3 pipeline.py report <project> <layer>
  python3 pipeline.py retry <project>
  python3 pipeline.py projects
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 确保 pipeline/ 在 sys.path
sys.path.insert(0, str(Path(__file__).parent))

from db import (
    init_db,
    create_run,
    update_run,
    get_run,
    get_latest_run,
    save_layer_result,
    get_layer_results,
)
from config import get_project, list_projects as list_project_names, load_projects

# Layer 导入 — 延迟加载避免循环
LAYER_ORDER = ["L1", "L2", "L3", "L4", "L5", "L6"]
MAX_L4_L5_CYCLES = 3


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def get_layer_instance(layer_name: str):
    """延迟加载 Layer 实例"""
    mapping = {
        "L1": ("layers.L1_analyze", "L1Analyze"),
        "L2": ("layers.L2_implement", "L2Implement"),
        "L3": ("layers.L3_build", "L3Build"),
        "L4": ("layers.L4_test", "L4Test"),
        "L5": ("layers.L5_fix", "L5Fix"),
        "L6": ("layers.L6_deploy", "L6Deploy"),
    }
    mod_name, cls_name = mapping[layer_name]
    import importlib

    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)()


def run_layer(layer_name, project_config, run_id, prev_results):
    """执行单层，处理重试"""
    layer = get_layer_instance(layer_name)

    # 前置检查
    ok, reason = layer.check_preconditions(prev_results)
    if not ok:
        log(f"  {layer_name} 前置条件未满足: {reason}")
        return None

    for attempt in range(1, layer.max_retries + 1):
        log(f"  {layer_name} attempt {attempt}/{layer.max_retries}")
        save_layer_result(run_id, layer_name, "RUNNING", attempt=attempt)

        try:
            result = layer.execute(project_config, prev_results)
        except Exception as e:
            result = __import__("layers.base", fromlist=["LayerResult"]).LayerResult(
                layer=layer_name, status="FAIL", error=str(e)
            )
            result.finish("FAIL", error=str(e))

        if result.finished_at is None:
            result.finish(result.status)

        save_layer_result(
            run_id,
            layer_name,
            result.status,
            attempt=attempt,
            report=result.report,
            error=result.error,
        )

        if layer.validate(result):
            log(f"  {layer_name} PASS")
            return result
        else:
            log(
                f"  {layer_name} FAIL (attempt {attempt}): {result.error or 'validation failed'}"
            )

    log(f"  {layer_name} FAILED after {layer.max_retries} attempts")
    return result


def cmd_run(args):
    """执行 pipeline"""
    project_name = args.project
    pc = get_project(project_name)
    if not pc:
        log(f"项目 {project_name} 不存在。可用: {list_project_names()}")
        sys.exit(1)

    # 确定执行范围
    if args.layer:
        layers = [args.layer]
    elif getattr(args, "from_layer", None):
        start_idx = LAYER_ORDER.index(args.from_layer)
        layers = LAYER_ORDER[start_idx:]
    else:
        layers = LAYER_ORDER[:]

    log(f"=== Pipeline: {project_name} | Layers: {' → '.join(layers)} ===")

    run_id = create_run(
        project_name, config=pc.__dict__ if hasattr(pc, "__dict__") else {}
    )
    prev_results = {}

    i = 0
    l4_l5_cycles = 0
    while i < len(layers):
        layer_name = layers[i]
        update_run(run_id, current_layer=layer_name)
        log(f"\n--- {layer_name} ---")

        result = run_layer(layer_name, pc, run_id, prev_results)

        if result is None:
            update_run(
                run_id, status="FAILED", finished_at=datetime.utcnow().isoformat()
            )
            log(f"Pipeline FAILED at {layer_name} (precondition)")
            sys.exit(1)

        if result.status == "PASS":
            prev_results[layer_name] = result
            # L4 pass → 跳过 L5，直接 L6
            if layer_name == "L4" and i + 1 < len(layers) and layers[i + 1] == "L5":
                log("  L4 PASS, 跳过 L5")
                i += 2  # 跳 L5
                l4_l5_cycles = 0
            else:
                i += 1
        elif result.status == "FAIL":
            # L4 fail → 进 L5 修复 → 回 L4
            if layer_name == "L4" and l4_l5_cycles < MAX_L4_L5_CYCLES:
                l4_l5_cycles += 1
                log(f"  L4→L5 修复循环 {l4_l5_cycles}/{MAX_L4_L5_CYCLES}")
                prev_results[layer_name] = result
                # 执行 L5
                l5_result = run_layer("L5", pc, run_id, prev_results)
                if l5_result and l5_result.status == "PASS":
                    prev_results["L5"] = l5_result
                    # 回到 L4 重测（不递增 i）
                    continue
                else:
                    update_run(
                        run_id,
                        status="FAILED",
                        finished_at=datetime.utcnow().isoformat(),
                    )
                    log("Pipeline FAILED: L5 修复失败")
                    sys.exit(1)
            else:
                update_run(
                    run_id, status="FAILED", finished_at=datetime.utcnow().isoformat()
                )
                log(f"Pipeline FAILED at {layer_name}")
                sys.exit(1)

    update_run(
        run_id,
        status="DONE",
        current_layer="DONE",
        finished_at=datetime.utcnow().isoformat(),
    )
    log(f"\n=== Pipeline DONE: {project_name} (run {run_id}) ===")

    # 保存总报告
    report_dir = Path(__file__).parent / "reports" / project_name
    report_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": run_id,
        "project": project_name,
        "layers": {
            k: {"status": v.status, "report": v.report} for k, v in prev_results.items()
        },
    }
    (report_dir / f"run-{run_id}-summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    log(f"报告: {report_dir}/run-{run_id}-summary.json")


def cmd_status(args):
    """查看状态"""
    if args.project:
        run = get_latest_run(args.project)
        if not run:
            print(f"No runs for {args.project}")
            return
        results = get_layer_results(run["id"])
        print(
            f"Project: {args.project} | Run: {run['id']} | Status: {run['status']} | Layer: {run['current_layer']}"
        )
        for r in results:
            print(f"  {r['layer']}: {r['status']} (attempt {r['attempt']})")
    else:
        for name in list_project_names():
            run = get_latest_run(name)
            status = (
                f"run {run['id']} | {run['status']} | {run['current_layer']}"
                if run
                else "no runs"
            )
            print(f"  {name}: {status}")


def cmd_report(args):
    """查看报告"""
    report_dir = Path(__file__).parent / "reports" / args.project
    if args.layer:
        # 查找最新的该层结果
        run = get_latest_run(args.project)
        if run:
            results = get_layer_results(run["id"])
            for r in results:
                if r["layer"] == args.layer:
                    print(
                        json.dumps(
                            json.loads(r["report"]) if r["report"] else {}, indent=2
                        )
                    )
                    return
        print(f"No {args.layer} result for {args.project}")
    else:
        # 列出所有报告文件
        if report_dir.exists():
            for f in sorted(report_dir.glob("*.json")):
                print(f"  {f.name}")
        else:
            print(f"No reports for {args.project}")


def cmd_retry(args):
    """重试失败的 pipeline"""
    run = get_latest_run(args.project)
    if not run:
        print(f"No runs for {args.project}")
        return
    if run["status"] != "FAILED":
        print(f"Latest run is {run['status']}, not FAILED")
        return
    failed_layer = run["current_layer"]
    log(f"Retrying {args.project} from {failed_layer}")
    # 模拟 --from 参数
    args.from_layer = failed_layer
    args.layer = None
    cmd_run(args)


def cmd_projects(args):
    """列出项目"""
    projects = load_projects()
    for name, pc in projects.items():
        print(f"  {name}: {pc.stack} → {pc.deploy} ({pc.path})")


def main():
    init_db()

    parser = argparse.ArgumentParser(description="Pipeline Infra CLI")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run")
    p_run.add_argument("project")
    p_run.add_argument("--layer", choices=LAYER_ORDER)
    p_run.add_argument("--from", dest="from_layer", choices=LAYER_ORDER)

    p_status = sub.add_parser("status")
    p_status.add_argument("project", nargs="?")

    p_report = sub.add_parser("report")
    p_report.add_argument("project")
    p_report.add_argument("layer", nargs="?", choices=LAYER_ORDER)

    p_retry = sub.add_parser("retry")
    p_retry.add_argument("project")

    sub.add_parser("projects")

    args = parser.parse_args()

    commands = {
        "run": cmd_run,
        "status": cmd_status,
        "report": cmd_report,
        "retry": cmd_retry,
        "projects": cmd_projects,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
