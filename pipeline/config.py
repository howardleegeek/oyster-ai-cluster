#!/usr/bin/env python3
"""项目配置加载"""
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BackendConfig:
    path: str
    cmd: str
    port: int
    health: str = "/health"

@dataclass
class FrontendConfig:
    type: str  # "react-vite", "static", "flutter"
    path: str = "."
    build: Optional[str] = None
    dev: Optional[str] = None
    serve: Optional[str] = None
    port: int = 5173

@dataclass
class ProjectConfig:
    name: str
    path: str
    stack: str
    deploy: str
    backend: Optional[BackendConfig] = None
    frontend: Optional[FrontendConfig] = None
    env_required: list = field(default_factory=list)
    test_urls: list = field(default_factory=list)
    test_flows: list = field(default_factory=list)
    llm_provider: str = "minimax"

def load_projects() -> dict[str, ProjectConfig]:
    config_path = Path(__file__).parent / "projects.yaml"
    with open(config_path) as f:
        data = yaml.safe_load(f)
    result = {}
    for name, d in data["projects"].items():
        be = d.get("backend")
        fe = d.get("frontend")
        result[name] = ProjectConfig(
            name=name,
            path=d["path"],
            stack=d["stack"],
            deploy=d["deploy"],
            backend=BackendConfig(**be) if be else None,
            frontend=FrontendConfig(**fe) if fe else None,
            env_required=d.get("env_required", []),
            test_urls=d.get("test_urls", []),
            test_flows=d.get("test_flows", []),
            llm_provider=d.get("llm_provider", "minimax"),
        )
    return result

def get_project(name: str) -> Optional[ProjectConfig]:
    return load_projects().get(name)

def list_projects() -> list[str]:
    return list(load_projects().keys())
