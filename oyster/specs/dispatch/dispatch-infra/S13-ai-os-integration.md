---
task_id: S13-ai-os-integration
project: dispatch-infra
priority: 1
depends_on: ["S10-infra-guardian", "S11-predictive-scheduling", "S12-code-self-audit"]
modifies:
  - infrastructure/ai_os/config/aios_integration.yaml
  - infrastructure/ai_os/scripts/aios_adapter.py
executor: glm
---

# AIOS Integration: 契约 + 配置 + 适配器

## 目标
实现 S13 AIOS 集成，**不写死任何路径/项目/规则**。所有可变项收敛到配置文件。

## 约束（关键）
- **不写死**：spec_id → project / bucket / event_type 映射必须来自配置
- **热更新**：适配器每次调用前 reload 配置
- **最小契约**：dispatch-infra 只需输出 RunResult JSON（字段可少）

## RunResult 最小契约

dispatch-infra 每个 spec run 只需产出 JSON：
```json
{
  "spec_id": "S10-infra-guardian",
  "tool": "dispatch-infra",
  "status": "ok|warn|fail",
  "summary": "一句话摘要",
  "metrics": { "latency_ms": 1234 },
  "findings": { "high": 0, "medium": 2, "low": 5 },
  "artifacts": [
    { "kind": "report_md", "path": "/abs/or/rel/path/to/report.md" }
  ],
  "timestamp": "2026-02-15T21:10:00-08:00"
}
```

## 具体改动

### 1. 配置文件：`infrastructure/ai_os/config/aios_integration.yaml`

```yaml
version: 1

paths:
  aios_root: "../infrastructure/ai_os"  # 相对本 repo 根；未来迁移只改这里
  events_dir: "events"
  projects_dir: "projects"
  config_dir: "config"

defaults:
  project: "Infra"
  outputs_buckets: ["ops", "infra", "misc", "bd", "content", "research"]
  timezone: "America/Los_Angeles"

routing:
  # spec_id 前缀 → project + event_type + outputs_bucket
  rules:
    - match:
        spec_prefix: "S10"
      route:
        project: "Infra"
        event_type: "guardian.check"
        bucket: "ops"

    - match:
        spec_prefix: "S12"
      route:
        project: "Infra"
        event_type: "audit.code"
        bucket: "infra"

    - match:
        spec_prefix: "S11"
      route:
        project: "Infra"
        event_type: "schedule.predict"
        bucket: "ops"

    - match:
        spec_prefix: "S02"
      route:
        project: "Infra"
        event_type: "agent.self_evolve"
        bucket: "infra"

tasks:
  enable: true
  idempotency_key:
    template: "{event_type}:{spec_id}:{date}"

dialogue:
  enable: true
  append_per_batch: true
```

### 2. 适配器：`infrastructure/ai_os/scripts/aios_adapter.py`

```python
#!/usr/bin/env python3
"""AIOS Adapter - 不写死任何路径/项目映射"""

import json
import yaml
from pathlib import Path
from datetime import datetime

class AIOSAdapter:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config()
        self.config = None
    
    def _find_config(self) -> str:
        """从当前目录向上查找 aios_integration.yaml"""
        # 动态查找，不写死路径
    
    def load_config(self) -> dict:
        """每次调用前 reload 配置（热更新）"""
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)
        return self.config
    
    def route(self, run_result: dict) -> dict:
        """根据 routing.rules 决定 project/bucket/event_type"""
        spec_id = run_result.get("spec_id", "")
        for rule in self.config["routing"]["rules"]:
            if spec_id.startswith(rule["match"]["spec_prefix"]):
                return rule["route"]
        # Fallback to defaults
        return {
            "project": self.config["defaults"]["project"],
            "event_type": "infra.run",
            "bucket": "ops"
        }
    
    def emit_event(self, run_result: dict, route: dict):
        """写入 events/YYYY-MM.ndjson (append-only)"""
        # 按配置路径写入，不写死
    
    def write_output(self, run_result: dict, route: dict):
        """写入 outputs/{bucket}/YYYY-MM-DD_slug/"""
    
    def upsert_task(self, run_result: dict, route: dict):
        """TASKS.md 幂等更新"""
    
    def append_dialogue(self, run_result: dict, route: dict):
        """DIALOGUE.md 追加"""
    
    def process(self, run_result_path: str):
        """主入口：读取 run_result.json → 路由 → 写入 AIOS"""
        self.load_config()
        
        with open(run_result_path) as f:
            run_result = json.load(f)
        
        route = self.route(run_result)
        self.emit_event(run_result, route)
        self.write_output(run_result, route)
        self.upsert_task(run_result, route)
        self.append_dialogue(run_result, route)


if __name__ == "__main__":
    import sys
    adapter = AIOSAdapter()
    adapter.process(sys.argv[1])  # python3 aios_adapter.py run_result.json
```

### 3. CLI 入口

```bash
# 手动测试
python3 infrastructure/ai_os/scripts/aios_adapter.py run_result.json

# 或在 dispatch-infra 中调用
```

## 文件清单

| 文件 | 操作 | 描述 |
|------|------|------|
| `infrastructure/ai_os/config/aios_integration.yaml` | 新建 | 唯一配置源 |
| `infrastructure/ai_os/scripts/aios_adapter.py` | 新建 | 适配器 |

## 验收标准

- [ ] 配置文件中定义所有 routing rules
- [ ] 适配器每次调用 reload 配置
- [ ] 不写死任何 spec_id → project 映射
- [ ] 能处理任意符合契约的 run_result.json
- [ ] 未来 infra 改动只需改配置

## 不要做

- ❌ 不在代码里写死 "Infra" / "guardian.check" 等字符串
- ❌ 不假设 ai_os 路径（必须从配置读）
- ❌ 不重建 TASKS/DIALOGUE 模板
- ❌ 不修改 dispatch-infra 内部逻辑
