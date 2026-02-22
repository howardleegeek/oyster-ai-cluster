"""MCP server post-cleanup validation utilities.

This module provides a lightweight, deterministic health check helper used by
tests to validate MCP server functionality after a cleanup phase. The goal is
to offer a small, dependency-free checker that can be run in unit tests without
spinning up real MCP servers.
"""

from typing import Dict, List, Optional


def _server_health_ok(health: Optional[str]) -> bool:
    """Return True if the given health state is considered OK.

    We treat common healthy indicators as OK. Any other value is considered a
    potential issue after a cleanup phase.
    """

    if health is None:
        return False
    health_l = str(health).lower()
    return health_l in {"ok", "healthy", "healthy_waiting"}


def validate_mcp_post_cleanup(state: Dict) -> Dict[str, object]:
    """Validate MCP server health after a cleanup.

    Expected input structure (flexible enough for tests):
    {
        "servers": [
            {"name": "server-a", "health": "healthy"},
            {"name": "server-b", "health": "ok"},
            ...
        ],
        "web3_integration": {"enabled": true|false}
    }

    The function returns a simple report:
    {
        "ok": true|false,
        "issues": ["description of issue", ...]
    }
    """

    issues: List[str] = []

    servers: List[Dict] = state.get("servers", []) or []
    for s in servers:
        name = s.get("name", "<unknown>")
        health = s.get("health")
        if not _server_health_ok(health):
            issues.append(f"Server '{name}' health is '{health}'")

    # If web3 integration is enabled, require all servers to be healthy.
    web3 = state.get("web3_integration", {})
    web3_enabled = bool(web3.get("enabled"))
    if web3_enabled and issues:
        # If there are issues, mark the overall result as not OK even if some
        # servers are healthy. This reflects a stricter post-cleanup guarantee
        # when Web3 integrations rely on MCP health.
        ok = False
    else:
        ok = len(issues) == 0

    return {"ok": ok, "issues": issues}
