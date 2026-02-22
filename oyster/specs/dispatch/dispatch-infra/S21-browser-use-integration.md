---
task_id: S21-browser-use-integration
project: dispatch-infra
priority: 1
depends_on: []
modifies:
  - dispatch/browser_agent.py
executor: glm
---

# Browser-Use Integration: 高级浏览器自动化

## 目标
集成 browser-use 到 dispatch，实现更强大的浏览器自动化能力

## 背景
- browser-use: 78k stars, Python 最好用的浏览器自动化库
- 支持 Playwright, 可视化提取, 多页处理

## 具体改动

### 1. 新增 browser_agent.py
```python
from browser_use import BrowserAgent, BrowserConfig

class DispatchBrowserAgent:
    """Dispatch 的浏览器自动化代理"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def execute_task(self, task: str, urls: list) -> dict:
        """执行浏览器任务"""
        agent = BrowserAgent(
            task=task,
            urls=urls,
            llm=self.config.get("llm", "claude-sonnet")
        )
        return agent.run()
    
    def extract_content(self, url: str, selector: str) -> str:
        """提取页面内容"""
    
    def take_screenshot(self, url: str) -> bytes:
        """截图"""
```

### 2. 配置
```json
{
  "browser_use": {
    "enabled": false,
    "headless": true,
    "timeout": 60,
    "max_steps": 10
  }
}
```

## 验收标准
- [ ] 能打开网页并执行任务
- [ ] 能提取内容
- [ ] 能截图
