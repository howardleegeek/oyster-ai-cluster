---
task_id: S26-opentelemetry-tracing
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/tracing.py
  - dispatch/tracing_config.json
executor: glm
---

# OpenTelemetry Tracing: 可观测性

## 目标
集成 OpenTelemetry + Traceloop 实现分布式追踪

## 背景
- 每个 spec 执行需要 trace
- 需要定位慢请求、失败根因
- 与现有 events 互补

## 具体改动

### 1. 新增 tracing.py
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

class Tracing:
    """分布式追踪"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.setup_provider()
    
    def setup_provider(self):
        """设置追踪 provider"""
        provider = TracerProvider()
        processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=self.config.get("endpoint"))
        )
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)
    
    def trace_task(self, task_id: str):
        """创建任务追踪"""
        return self.tracer.start_as_current_span(
            f"task:{task_id}",
            attributes={
                "task.id": task_id,
                "service": "dispatch"
            }
        )
    
    def emit_event(self, event_type: str, data: dict):
        """添加事件到 trace"""
        # 与 AIOS events 互补
```

### 2. 配置
```json
{
  "enabled": false,
  "endpoint": "http://localhost:4318",
  "service_name": "dispatch",
  "sample_rate": 0.1,
  "export_batch_size": 100
}
```

### 3. Dashboard 指标
- Top Slow Spans
- Error Rate by Task
- Latency Distribution

## 验收标准
- [ ] 能追踪任务执行
- [ ] 能记录慢请求
- [ ] 能关联错误
