---
task_id: S25-litellm-gateway
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/llm_gateway.py
  - dispatch/llm_config.json
executor: glm
---

# LiteLLM Gateway: 统一模型调用 + 成本治理

## 目标
集成 LiteLLM 作为统一模型网关，实现：
1. 统一 API（OpenAI 格式）
2. 成本追踪
3. 智能路由
4. 限流/配额

## 背景
- LiteLLM: 统一 100+ 模型 API
- 支持 cost tracking, retry, fallback
- 适合多模型/多 agent 环境

## 具体改动

### 1. 新增 llm_gateway.py
```python
import litellm
from litellm import completion, acompletion

class LLMGateway:
    """统一 LLM 网关"""
    
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        litellm.drop_params = True
        litellm.set_verbose = False
    
    def complete(self, model: str, messages: list, **kwargs) -> dict:
        """同步调用"""
        response = completion(
            model=model,
            messages=messages,
            **self.config.get("default_params", {}),
            **kwargs
        )
        return self._parse_response(response)
    
    async def acomplete(self, model: str, messages: list, **kwargs) -> dict:
        """异步调用"""
        response = await acompletion(
            model=model,
            messages=messages,
            **self.config.get("default_params", {}),
            **kwargs
        )
        return self._parse_response(response)
    
    def _parse_response(self, response) -> dict:
        """解析响应"""
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "cost": self.calculate_cost(response),
            "latency_ms": response._response_ms
        }
    
    def calculate_cost(self, response) -> float:
        """计算成本"""
        # LiteLLM 内置 cost tracking
        return litellm.completion_cost(completion_response=response)
    
    def router(self, task_type: str) -> str:
        """智能路由"""
        routing = self.config.get("routing", {})
        return routing.get(task_type, self.config.get("default_model"))
```

### 2. 配置 llm_config.json
```json
{
  "default_model": "claude-sonnet-4-20250514",
  "routing": {
    "simple": "claude-haiku-3-20250207",
    "medium": "claude-sonnet-4-20250514",
    "complex": "claude-opus-4-20250514",
    "code": "claude-sonnet-4-20250514",
    "reasoning": "deepseek/deepseek-chat"
  },
  "fallback": {
    "claude-opus-4-20250514": "claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514": "claude-haiku-3-20250207"
  },
  "budget": {
    "daily_limit_usd": 100,
    "warn_at_usd": 80
  },
  "rate_limit": {
    "claude-opus-4-20250514": {"requests_per_minute": 10},
    "claude-sonnet-4-20250514": {"requests_per_minute": 50}
  },
  "providers": {
    "openai": {"api_key": "os.environ/OPENAI_API_KEY"},
    "anthropic": {"api_key": "os.environ/ANTHROPIC_API_KEY"},
    "deepseek": {"api_key": "os.environ.DEEPSEEK_API_KEY"}
  }
}
```

### 3. 成本事件
每次调用写入 AIOS 事件：
```python
def emit_llm_event(response: dict, task_id: str):
    event = {
        "ts": datetime.now().isoformat(),
        "type": "llm.call",
        "actor": "dispatch",
        "project": "Infra",
        "summary": f"{response['model']} - ${response['cost']:.4f}",
        "refs": {"task_id": task_id},
        "meta": {
            "model": response["model"],
            "cost_usd": response["cost"],
            "latency_ms": response["latency_ms"],
            "tokens": response["usage"]["total_tokens"]
        }
    }
```

### 4. Dashboard 指标
```
- 今日成本: $XX.XX
- 本周成本: $XXX.XX
- 按模型分布
- 按任务分布
- 超预算警告
```

## 文件清单

| 文件 | 描述 |
|------|------|
| `dispatch/llm_gateway.py` | LiteLLM 网关 |
| `dispatch/llm_config.json` | 配置文件 |

## 验收标准

- [ ] 能统一调用多模型
- [ ] 能追踪成本
- [ ] 能自动 fallback
- [ ] 能限流
- [ ] 能写入事件

## 不做

- ❌ 不存储实际 API keys
- ❌ 不修改现有 executor
