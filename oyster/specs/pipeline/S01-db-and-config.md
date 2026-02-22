---
task_id: S01-db-and-config
project: pipeline
priority: 1
depends_on: []
modifies: ["dispatch/pipeline/db.py", "dispatch/pipeline/config.py", "dispatch/pipeline/projects.yaml"]
executor: glm
---

## 目标
创建 pipeline 基础：SQLite 数据库管理 + 项目配置系统 + projects.yaml

## 要创建的文件

### 1. dispatch/pipeline/db.py
```python
#!/usr/bin/env python3
"""Pipeline 数据库管理"""
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

DB_PATH = Path(__file__).parent / "pipeline.db"

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                current_layer TEXT DEFAULT 'L1',
                status TEXT DEFAULT 'RUNNING' CHECK(status IN ('RUNNING','DONE','FAILED')),
                retry_count INTEGER DEFAULT 0,
                config JSON
            );
            CREATE TABLE IF NOT EXISTS layer_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                layer TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('RUNNING','PASS','FAIL','SKIPPED')),
                attempt INTEGER DEFAULT 1,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                report JSON,
                error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_runs_project ON runs(project);
            CREATE INDEX IF NOT EXISTS idx_lr_run ON layer_results(run_id);
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_run(project: str, config: dict = None) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO runs (project, started_at, config) VALUES (?, ?, ?)",
            (project, datetime.utcnow().isoformat(), json.dumps(config or {}))
        )
        return cur.lastrowid

def update_run(run_id: int, **kwargs):
    with get_db() as conn:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [run_id]
        conn.execute(f"UPDATE runs SET {sets} WHERE id=?", vals)

def get_run(run_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None

def get_latest_run(project: str) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE project=? ORDER BY id DESC LIMIT 1", (project,)
        ).fetchone()
        return dict(row) if row else None

def save_layer_result(run_id: int, layer: str, status: str, attempt: int = 1,
                      report: dict = None, error: str = None):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO layer_results (run_id, layer, status, attempt, started_at, finished_at, report, error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, layer, status, attempt, datetime.utcnow().isoformat(),
             datetime.utcnow().isoformat() if status != 'RUNNING' else None,
             json.dumps(report or {}), error)
        )

def get_layer_results(run_id: int) -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM layer_results WHERE run_id=? ORDER BY id", (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]
```

### 2. dispatch/pipeline/config.py
```python
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
```

### 3. dispatch/pipeline/projects.yaml
```yaml
projects:
  clawvision:
    path: ~/Downloads/clawvision-org/
    stack: static-html
    deploy: vercel
    frontend:
      type: static
      path: "."
      serve: "npx serve ."
      port: 3000
    test_urls: ["/", "/api.html", "/blog.html", "/map.html", "/whitepaper.html"]

  gem-platform:
    path: ~/Downloads/gem-platform/
    stack: fastapi-react
    deploy: vercel+fly
    backend:
      path: backend/
      cmd: "uvicorn app.main:app --host 0.0.0.0"
      port: 8000
      health: "/health"
    frontend:
      type: react-vite
      path: lumina/
      build: "npm run build"
      dev: "npm run dev"
      port: 5173
    env_required: [DATABASE_URL, REDIS_URL, STRIPE_KEY, SOLANA_RPC]
    test_flows:
      - name: "register-login-browse"
        steps: ["POST /auth/register", "POST /auth/login", "GET /packs"]

  clawmarketing:
    path: ~/Downloads/clawmarketing/
    stack: fastapi-react
    deploy: docker-compose
    backend:
      path: backend/
      cmd: "uvicorn app.main:app --host 0.0.0.0"
      port: 8000
      health: "/health"
    frontend:
      type: react-vite
      path: frontend/
      build: "npm run build"
      dev: "npm run dev"
      port: 5173
    env_required: [DATABASE_URL, REDIS_URL, MINIMAX_API_KEY]
    llm_provider: minimax

  clawphones:
    path: ~/.openclaw/workspace/
    stack: fastapi-mobile
    deploy: fly
    backend:
      path: proxy/
      cmd: "python server.py"
      port: 8080
      health: "/health"
    env_required: [DEEPSEEK_KEY, KIMI_KEY, CLAUDE_KEY]

  oysterworld:
    path: ~/Downloads/oysterworld/
    stack: node-prototype
    deploy: fly+vercel
    backend:
      path: prototype/relay/
      cmd: "node server.js"
      port: 8787
      health: "/health"
    frontend:
      type: static
      path: prototype/node-web/
      serve: "npx serve ."
      port: 3000
```

## 验收标准
- [ ] `python3 -c "from db import init_db; init_db()"` 在 pipeline/ 下执行成功
- [ ] `python3 -c "from config import list_projects; print(list_projects())"` 输出 5 个项目名
- [ ] pipeline.db 文件被创建，两张表 schema 正确

## 不要做
- 不要创建 pipeline.py CLI（S03 做）
- 不要创建 Layer 类（S02 做）
- 不要修改 dispatch/ 下任何已有文件
