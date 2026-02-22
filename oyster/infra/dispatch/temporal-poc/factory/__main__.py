"""
Run the Deep Think Factory.

Usage:
    # Default config (ClawMarketing + Shell pilot)
    python -m factory

    # Custom config
    python -m factory --config factory.yaml

    # Limited run (2 hours)
    python -m factory --hours 2

    # Dry run (1 cycle only)
    python -m factory --cycles 1
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from .config import FactoryConfig
from .orchestrator import FactoryOrchestrator, run_factory


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deep Think Factory — 24h Autonomous Development"
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to factory.yaml config file",
        default=None,
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=24.0,
        help="Maximum runtime in hours (default: 24)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="Run exactly N cycles then stop (0 = unlimited)",
    )
    parser.add_argument(
        "--project",
        help="Run only this project (default: all configured)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    # Logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Load config
    if args.config:
        config = FactoryConfig.from_yaml(args.config)
    else:
        # Check for factory.yaml next to this file
        default_yaml = Path(__file__).parent / "factory.yaml"
        if default_yaml.exists():
            config = FactoryConfig.from_yaml(default_yaml)
        else:
            config = FactoryConfig.default()

    # Filter to single project if requested
    if args.project:
        config.projects = [
            p for p in config.projects if p.name == args.project
        ]
        if not config.projects:
            print(f"Error: project '{args.project}' not found in config")
            sys.exit(1)

    # Override cycle limit if requested
    if args.cycles > 0:
        config.max_cycles_per_day = args.cycles

    print(f"Deep Think Factory starting...")
    print(f"  Projects: {[p.name for p in config.projects]}")
    print(f"  Max hours: {args.hours}")
    print(f"  Max cycles: {config.max_cycles_per_day}")
    print()

    asyncio.run(run_factory(config=config, max_hours=args.hours))


if __name__ == "__main__":
    main()
