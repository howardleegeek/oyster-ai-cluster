#!/usr/bin/env python3
"""Pipeline 集成测试"""

import sys
import json
import subprocess
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent.parent
PIPELINE_PY = PIPELINE_DIR / "pipeline.py"


def run_cmd(cmd: str) -> tuple[int, str, str]:
    r = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(PIPELINE_DIR),
        timeout=120,
    )
    return r.returncode, r.stdout, r.stderr


def test_projects_list():
    """测试 projects 命令"""
    code, out, err = run_cmd(f"python3 {PIPELINE_PY} projects")
    assert code == 0, f"projects 命令失败: {err}"
    assert "clawvision" in out, f"clawvision 不在列表中: {out}"
    assert "gem-platform" in out
    assert "clawmarketing" in out
    assert "clawphones" in out
    assert "oysterworld" in out
    print("PASS: projects list")


def test_status_empty():
    """测试空状态"""
    code, out, err = run_cmd(f"python3 {PIPELINE_PY} status")
    assert code == 0, f"status 命令失败: {err}"
    print("PASS: status empty")


def test_l1_clawvision():
    """测试 L1 对 clawvision 的分析"""
    code, out, err = run_cmd(f"python3 {PIPELINE_PY} run clawvision --layer L1")
    assert code == 0, f"L1 失败: {err}\n{out}"

    # 检查报告
    report_file = PIPELINE_DIR / "reports" / "clawvision" / "L1-gap-report.json"
    assert report_file.exists(), "L1 报告未生成"

    report = json.loads(report_file.read_text())
    assert report["project"] == "clawvision"
    assert report["files_scanned"] > 0, "没扫描到文件"
    assert "gap_by_type" in report
    print(
        f"PASS: L1 clawvision — {report['files_scanned']} files, {report['total_gaps']} gaps"
    )


def test_l1_gem_platform():
    """测试 L1 对 gem-platform 的分析"""
    code, out, err = run_cmd(f"python3 {PIPELINE_PY} run gem-platform --layer L1")
    assert code == 0, f"L1 失败: {err}\n{out}"

    report_file = PIPELINE_DIR / "reports" / "gem-platform" / "L1-gap-report.json"
    assert report_file.exists()

    report = json.loads(report_file.read_text())
    assert report["files_scanned"] > 0
    assert len(report.get("endpoints", [])) > 0, "应该检测到 API endpoints"
    print(
        f"PASS: L1 gem-platform — {report['files_scanned']} files, {len(report['endpoints'])} endpoints"
    )


def test_status_after_run():
    """测试运行后的状态"""
    code, out, err = run_cmd(f"python3 {PIPELINE_PY} status clawvision")
    assert code == 0
    assert "L1" in out
    print("PASS: status after run")


def test_db_integrity():
    """测试数据库完整性"""
    import sqlite3

    db_path = PIPELINE_DIR / "pipeline.db"
    assert db_path.exists(), "pipeline.db 不存在"

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # 检查 runs 表
    runs = conn.execute("SELECT * FROM runs").fetchall()
    assert len(runs) > 0, "runs 表为空"

    # 检查 layer_results 表
    results = conn.execute("SELECT * FROM layer_results").fetchall()
    assert len(results) > 0, "layer_results 表为空"

    conn.close()
    print(f"PASS: DB integrity — {len(runs)} runs, {len(results)} layer results")


def main():
    tests = [
        test_projects_list,
        test_status_empty,
        test_l1_clawvision,
        test_l1_gem_platform,
        test_status_after_run,
        test_db_integrity,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} — {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
