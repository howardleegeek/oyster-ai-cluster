#!/usr/bin/env python3
"""Capabilities-aware scheduling for dispatch"""

from typing import List, Dict, Optional
import json
from pathlib import Path

# Define node capabilities
NODE_CAPABILITIES = {
    "oci-paid-1": {
        "slots": 40,
        "capabilities": ["python", "node", "browser", "docker"],
        "arch": "x86_64",
    },
    "oci-paid-3": {
        "slots": 48,
        "capabilities": ["python", "node", "browser", "docker"],
        "arch": "x86_64",
    },
    "oci-arm-1": {
        "slots": 20,
        "capabilities": ["python", "node", "arm64"],
        "arch": "arm64",
    },
    "mac2": {
        "slots": 5,
        "capabilities": ["python", "node", "browser"],
        "arch": "x86_64",
    },
}

# Task requirements
TASK_REQUIREMENTS = {
    "browser": ["browser"],
    "ios": ["node", "arm64"],
    "android": ["node", "docker"],
    "default": ["python", "node"],
}

def get_matching_nodes(task_capabilities: List[str]) -> List[str]:
    """Find nodes that match task capabilities"""
    matching = []
    for node, caps in NODE_CAPABILITIES.items():
        if all(cap in caps["capabilities"] for cap in task_capabilities):
            matching.append(node)
    return matching

def select_best_node(task_capabilities: List[str], available_nodes: List[Dict]) -> Optional[Dict]:
    """Select best node based on capabilities and availability"""
    required = set(task_capabilities)
    
    for node in available_nodes:
        node_caps = NODE_CAPABILITIES.get(node["name"], {}).get("capabilities", [])
        if all(cap in node_caps for cap in required):
            return node
    return None

if __name__ == "__main__":
    # Test
    print("Testing capabilities matching...")
    nodes = get_matching_nodes(["browser"])
    print(f"Nodes with browser: {nodes}")
    
    result = select_best_node(["browser"], [
        {"name": "oci-paid-1", "slots": 40},
        {"name": "oci-paid-3", "slots": 48},
    ])
    print(f"Best node: {result}")
