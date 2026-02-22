#!/usr/bin/env python3
"""Crontab management for Night Shift Scheduler"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List

# Cron job 标识
CRON_COMMENT = "# night-shift-scheduler"
CRON_TAG = "night-shift-scheduler"


def get_python_executable() -> str:
    """获取 Python 可执行文件路径

    Returns:
        python_path: Python 可执行文件路径
    """
    return sys.executable


def get_scheduler_path() -> Path:
    """获取调度器脚本路径

    Returns:
        scheduler_path: 调度器脚本路径
    """
    return Path(__file__).parent / "scheduler.py"


def install_cron(
    night_batch_cron: Optional[str] = None,
    ci_scan_cron: Optional[str] = None,
    log_path: Optional[str] = None
) -> bool:
    """安装 cron job

    Args:
        night_batch_cron: 夜间批量任务的 cron 表达式，默认 "0 1 * * *" (每天 1:00)
        ci_scan_cron: CI 扫描任务的 cron 表达式，默认 "*/15 * * * *" (每 15 分钟)
        log_path: 日志文件路径

    Returns:
        success: 是否成功安装
    """
    # 默认值
    if night_batch_cron is None:
        night_batch_cron = "0 1 * * *"
    if ci_scan_cron is None:
        ci_scan_cron = "*/15 * * * *"

    python_path = get_python_executable()
    scheduler_path = get_scheduler_path()

    if log_path is None:
        log_path = str(Path(__file__).parent / "night_shift.log")

    # 构建 cron 命令
    cron_entries = [
        # 夜间批量任务 (1:00 AM)
        f"{night_batch_cron} cd {Path.cwd()} && {python_path} {scheduler_path} run_batch night_worker 3 >> {log_path} 2>&1 {CRON_COMMENT} night_batch",
        # CI 失败扫描 (每 15 分钟)
        f"{ci_scan_cron} cd {Path.cwd()} && {python_path} {scheduler_path} scan_ci ci_worker 2 >> {log_path} 2>&1 {CRON_COMMENT} ci_scan",
    ]

    # 获取现有 cron
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=True
        )
        existing_cron = result.stdout
    except subprocess.CalledProcessError:
        # 没有现有 cron
        existing_cron = ""

    # 移除旧的调度器 cron
    lines = [line for line in existing_cron.split('\n') if CRON_TAG not in line]

    # 添加新的 cron
    new_cron = '\n'.join(lines + cron_entries + [''])

    # 写入 crontab
    try:
        subprocess.run(
            ["crontab", "-"],
            input=new_cron,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install cron: {e}")
        print(f"stderr: {e.stderr}")
        return False


def remove_cron() -> bool:
    """移除 cron job

    Returns:
        success: 是否成功移除
    """
    try:
        # 获取现有 cron
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=True
        )
        existing_cron = result.stdout
    except subprocess.CalledProcessError:
        # 没有现有 cron
        return True

    # 移除调度器 cron
    lines = [line for line in existing_cron.split('\n') if CRON_TAG not in line]

    # 如果没有剩余内容，删除 crontab
    if not any(line.strip() for line in lines):
        try:
            subprocess.run(
                ["crontab", "-r"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    # 否则写入过滤后的 cron
    new_cron = '\n'.join(lines)

    try:
        subprocess.run(
            ["crontab", "-"],
            input=new_cron,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to remove cron: {e}")
        print(f"stderr: {e.stderr}")
        return False


def list_cron() -> List[dict]:
    """列出当前安装的调度器 cron job

    Returns:
        cron_jobs: cron job 列表
    """
    cron_jobs = []

    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=True
        )
        existing_cron = result.stdout
    except subprocess.CalledProcessError:
        return cron_jobs

    for line in existing_cron.split('\n'):
        if CRON_TAG in line:
            parts = line.split()
            if len(parts) >= 6:
                cron_expr = ' '.join(parts[:5])
                command = ' '.join(parts[5:])
                job_type = "ci_scan" if "ci_scan" in line else "night_batch"
                cron_jobs.append({
                    'cron_expr': cron_expr,
                    'command': command,
                    'type': job_type
                })

    return cron_jobs


def verify_cron() -> bool:
    """验证 cron job 是否正确安装

    Returns:
        is_valid: 是否有效
    """
    cron_jobs = list_cron()

    if not cron_jobs:
        return False

    # 检查是否有两种类型的 job
    job_types = {job['type'] for job in cron_jobs}
    return 'night_batch' in job_types and 'ci_scan' in job_types


def show_cron_status():
    """显示 cron 状态"""
    cron_jobs = list_cron()

    if not cron_jobs:
        print("No night shift scheduler cron jobs installed")
    else:
        print(f"Found {len(cron_jobs)} cron job(s):")
        for job in cron_jobs:
            print(f"  [{job['type']}] {job['cron_expr']}")
            print(f"    {job['command']}")

    is_valid = verify_cron()
    print(f"\nStatus: {'Valid' if is_valid else 'Invalid (missing jobs)'}")


def main():
    """主函数 - 用于命令行操作"""
    import argparse

    parser = argparse.ArgumentParser(description="Night Shift Scheduler Cron Management")
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # install 命令
    install_parser = subparsers.add_parser('install', help='Install cron jobs')
    install_parser.add_argument('--night-cron', help='Night batch cron expression (default: "0 1 * * *")')
    install_parser.add_argument('--ci-cron', help='CI scan cron expression (default: "*/15 * * * *")')
    install_parser.add_argument('--log', help='Log file path')

    # remove 命令
    subparsers.add_parser('remove', help='Remove cron jobs')

    # list 命令
    subparsers.add_parser('list', help='List cron jobs')

    # status 命令
    subparsers.add_parser('status', help='Show cron status')

    args = parser.parse_args()

    if args.command == 'install':
        success = install_cron(
            night_batch_cron=args.night_cron,
            ci_scan_cron=args.ci_cron,
            log_path=args.log
        )
        if success:
            print("Cron jobs installed successfully")
            show_cron_status()
        else:
            print("Failed to install cron jobs")
            sys.exit(1)

    elif args.command == 'remove':
        success = remove_cron()
        if success:
            print("Cron jobs removed successfully")
        else:
            print("Failed to remove cron jobs")
            sys.exit(1)

    elif args.command == 'list':
        cron_jobs = list_cron()
        if not cron_jobs:
            print("No cron jobs installed")
        else:
            print(json.dumps(cron_jobs, indent=2))

    elif args.command == 'status':
        show_cron_status()

    else:
        parser.print_help()


if __name__ == '__main__':
    import json
    main()
