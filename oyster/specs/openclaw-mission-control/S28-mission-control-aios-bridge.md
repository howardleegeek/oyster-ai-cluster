---
task_id: S28-mission-control-aios-bridge
project: openclaw-mission-control
priority: 1
depends_on: []
modifies:
  - openclaw-mission-control/backend/app/api/aios.py
  - openclaw-mission-control/backend/app/services/aios_fs.py
  - openclaw-mission-control/frontend/src/app/aios/page.tsx
executor: glm
---

# Mission Control + AIOS Bridge: AIOS 作为数据源

## 目标
把 AIOS (events/tasks/outputs) 接进 Mission Control，作为数据真相来源

## 背景
- Mission Control: 已有 FastAPI + Next.js UI
- AIOS: events/tasks/outputs 系统
- 需要：双层模型 - UI 走 MC DB，真相走 AIOS 文件系统

## 具体改动

### 1. 后端：新增 AIOS Router

```python
# backend/app/api/aios.py
from fastapi import APIRouter, Query
from ..services.ai_os_fs import AIOSFilesystem

router = APIRouter(prefix="/api/v1/aios", tags=["AIOS"])
aios = AIOSFilesystem()

@router.get("/projects")
async def list_projects():
    """列 projects"""
    return aios.list_projects()

@router.get("/events")
async def list_events(
    project: str = Query(None),
    event_type: str = Query(None),
    limit: int = Query(100)
):
    """列 events (NDJSON tail)"""
    return aios.list_events(project, event_type, limit)

@router.get("/tasks")
async def list_tasks(project: str = Query(...)):
    """列 TASKS"""
    return aios.list_tasks(project)

@router.get("/outputs")
async def list_outputs(
    project: str = Query(...),
    kind: str = Query(None),
    limit: int = Query(20)
):
    """列 outputs"""
    return aios.list_outputs(project, kind, limit)

@router.post("/events/append")
async def append_event(event: dict):
    """追加 event (append-only)"""
    return aios.append_event(event)

@router.post("/tasks/upsert")
async def upsert_task(project: str, task: dict):
    """幂等更新 TASKS"""
    return aios.upsert_task(project, task)
```

### 2. 服务层：AIOS Filesystem

```python
# backend/app/services/ai_os_fs.py
import os
import json
from pathlib import Path
from datetime import datetime

class AIOSFilesystem:
    def __init__(self, root: str = None):
        self.root = Path(os.environ.get("AIOS_ROOT", "/Users/howardli/Downloads/infrastructure/ai_os"))
    
    def list_projects(self) -> list:
        """列 projects 目录"""
        projects_dir = self.root / "projects"
        return [p.name for p in projects_dir.iterdir() if p.is_dir()]
    
    def list_events(self, project=None, event_type=None, limit=100) -> list:
        """tail events/YYYY-MM.ndjson"""
        events_file = self.root / "events" / f"{datetime.now().strftime('%Y-%m')}.ndjson"
        if not events_file.exists():
            return []
        
        with open(events_file) as f:
            lines = f.readlines()[-limit:]
        
        events = [json.loads(l) for l in lines if l.strip()]
        
        if project:
            events = [e for e in events if e.get("project") == project]
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        
        return events
    
    def list_tasks(self, project: str) -> dict:
        """解析 TASKS.md"""
        tasks_file = self.root / "projects" / project / "TASKS.md"
        if not tasks_file.exists():
            return {"P0": [], "P1": [], "P2": [], "Done": []}
        
        # 简单解析：- [ ] P0 / - [x] Done
        # 返回结构化
        return {"tasks": [], "metadata": {}}
    
    def list_outputs(self, project: str, kind=None, limit=20) -> list:
        """扫描 outputs/"""
        outputs_dir = self.root / "projects" / project / "outputs"
        if not outputs_dir.exists():
            return []
        
        results = []
        for kind_dir in outputs_dir.iterdir():
            if kind and kind_dir.name != kind:
                continue
            for date_dir in sorted(kind_dir.iterdir(), reverse=True)[:limit]:
                results.append({
                    "path": str(date_dir.relative_to(self.root)),
                    "date": date_dir.name,
                    "kind": kind_dir.name
                })
        return results
    
    def append_event(self, event: dict) -> dict:
        """追加 NDJSON"""
        events_file = self.root / "events" / f"{datetime.now().strftime('%Y-%m')}.ndjson"
        events_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(events_file, "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        
        return {"status": "ok"}
    
    def upsert_task(self, project: str, task: dict) -> dict:
        """幂等更新 TASKS.md"""
        # 按 idempotency_key 检查，存在则跳过
        return {"status": "ok"}
```

### 3. 前端：新增 AIOS 页面

```typescript
// frontend/src/app/aios/page.tsx
"use client"

import { useState, useEffect } from 'react'

export default function AIOSPage() {
  const [projects, setProjects] = useState<string[]>([])
  const [selectedProject, setSelectedProject] = useState('Infra')
  const [events, setEvents] = useState<any[]>([])
  const [tasks, setTasks] = useState<any>({})
  const [outputs, setOutputs] = useState<any[]>([])
  
  useEffect(() => {
    // 加载数据
    fetch(`/api/v1/aios/projects`).then(r => r.json()).then(setProjects)
  }, [])
  
  useEffect(() => {
    if (!selectedProject) return
    Promise.all([
      fetch(`/api/v1/aios/events?project=${selectedProject}&limit=50`).then(r => r.json()),
      fetch(`/api/v1/aios/tasks?project=${selectedProject}`).then(r => r.json()),
      fetch(`/api/v1/aios/outputs?project=${selectedProject}`).then(r => r.json()),
    ]).then(([e, t, o]) => {
      setEvents(e)
      setTasks(t)
      setOutputs(o)
    })
  }, [selectedProject])
  
  return (
    <div className="p-4">
      <h1>AIOS Dashboard</h1>
      
      {/* Projects Tabs */}
      <div className="flex gap-2 mb-4">
        {projects.map(p => (
          <button key={p} onClick={() => setSelectedProject(p)}
            className={p === selectedProject ? "bg-blue-500 text-white" : "bg-gray-200"}>
            {p}
          </button>
        ))}
      </div>
      
      {/* Events Feed */}
      <div className="mb-4">
        <h2>Recent Events</h2>
        {events.slice(0, 10).map((e, i) => (
          <div key={i} className="border p-2 mb-1">
            <span className="text-xs">{e.ts}</span>
            <span className="ml-2 font-bold">{e.type}</span>
            <span className="ml-2">{e.summary}</span>
          </div>
        ))}
      </div>
      
      {/* Tasks */}
      <div className="mb-4">
        <h2>Tasks</h2>
        {/* 简化展示 */}
      </div>
      
      {/* Outputs */}
      <div>
        <h2>Outputs</h2>
        {outputs.map((o, i) => (
          <div key={i} className="border p-2 mb-1">
            {o.kind} - {o.date}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 4. 配置

```bash
# openclaw-mission-control/.env 新增
AIOS_ROOT=/Users/howardli/Downloads/infrastructure/ai_os
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `backend/app/api/aios.py` | 新建 | AIOS Router |
| `backend/app/services/aios_fs.py` | 新建 | 文件系统服务 |
| `frontend/src/app/aios/page.tsx` | 新建 | AIOS 页面 |

## 验收标准

- [ ] 能列 projects
- [ ] 能显示 events feed
- [ ] 能显示 tasks
- [ ] 能列 outputs
- [ ] 能追加 event

## 不做

- ❌ 不改 Mission Control 原有 DB
- ❌ 不删除已有功能
- ❌ 不改 AIOS 原有结构
