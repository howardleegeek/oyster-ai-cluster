---
task_id: S015-pipeline-scheduler
project: article-pipeline
priority: 0
estimated_minutes: 20
depends_on: ["S014-pipeline-orchestrator"]
modifies: ["oyster/social/article-pipeline/scheduler.py"]
executor: glm
---

## 目标
Schedule pipeline runs. Default: 3x daily (9am, 1pm, 6pm Beijing time).

## 约束
- Python 3.11+
- Use APScheduler or simple asyncio loop with sleep
- Schedule from env: PIPELINE_SCHEDULE (default: "09:00,13:00,18:00")
- Timezone: Asia/Shanghai
- On each trigger: call PipelineOrchestrator.run()
- Log each run result
- Graceful shutdown on SIGTERM/SIGINT
- Also support one-shot mode: `python -m article_pipeline.scheduler --once`
- Generate launchd plist for macOS auto-start

## 验收标准
- [ ] PipelineScheduler class with `async def start()`
- [ ] Runs at configured times in correct timezone
- [ ] --once mode for manual trigger
- [ ] Graceful shutdown
- [ ] launchd plist template in repo
- [ ] pytest test passes

## 不要做
- No systemd (macOS only for now)
- No web dashboard
