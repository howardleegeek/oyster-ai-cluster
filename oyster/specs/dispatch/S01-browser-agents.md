---
task_id: S01-browser-agents
project: dispatch
priority: 1
depends_on: []
modifies: ["dispatch/slot_agent.py", "dispatch/task-wrapper.sh"]
executor: glm
---

## 目标
全面升级 Slot Agents，赋予完整的浏览器自动化能力（视觉理解、页面交互、端到端测试）

## 约束
- 保持现有 Agent 身份系统不变
- 不破坏现有 dispatch 机制
- 浏览器通过 CDP 连接，支持远程控制
- 支持视觉理解和 UI 验证

## 具体改动

### 1. 升级 slot_agent.py - 浏览器能力注入
每个 Slot Agent 新增浏览器工具箱：
- `browser_navigate(url)` - 导航到 URL
- `browser_snapshot()` - 获取页面 accessibility tree
- `browser_screenshot()` - 获取页面截图
- `browser_click(selector)` - 点击元素
- `browser_type(selector, text)` - 输入文本
- `browser_query(pattern)` - 查询页面内容
- `browser_errors()` - 获取 JS 错误
- `browser_console()` - 获取 console 日志
- `browser_wait(text)` - 等待文本出现
- `browser_evaluate(js)` - 执行 JS

### 2. Agent 身份扩展 - 浏览器专家
扩展 AGENT_IDENTITIES，新增浏览器相关 specialty：
```python
AGENT_IDENTITIES = {
    0: {"name": "Alpha", "emoji": "🐺", "role": "Leader", "specialty": "Architecture"},
    1: {"name": "Beta", "emoji": "⚡", "role": "Executor", "specialty": "Backend"},
    2: {"name": "Gamma", "emoji": "🎨", "role": "Designer", "specialty": "Frontend"},
    3: {"name": "Omega", "emoji": "🖼️", "role": "Visual Engineer", "specialty": "Browser Automation"},
    4: {"name": "Pixel", "emoji": "🔍", "role": "QA Engineer", "specialty": "E2E Testing"},
    # ... 继续扩展到 37 个
}
```

### 3. 浏览器 MCP Server
创建 browser_mcp.py - MCP 协议暴露浏览器能力：
- 标准 MCP tools 接口
- 支持本地 CDP (localhost:9222) 和远程 CDP
- 连接池管理
- 错误重试和健康检查

### 4. 视觉理解能力
Agent 新增视觉理解方法：
- `analyze_screenshot()` - 分析截图内容
- `validate_ui(expected_elements)` - 验证 UI 元素存在
- `compare_screenshots(before, after)` - 截图对比
- `find_element(visual_description)` - 通过视觉描述找到元素

### 5. 端到端测试能力
- `run_e2e_test(test_spec)` - 执行 E2E 测试
- `validate_no_errors()` - 验证页面无 JS 错误
- `validate_console(allowed_levels)` - 验证 console 级别
- `capture_test_report()` - 捕获测试报告

### 6. 任务 wrapper 增强
task-wrapper.sh 新增：
- 浏览器测试自动运行
- 截图失败自动保存
- console 错误自动报告

## 验收标准
- [ ] Slot Agent 能导航到任意 URL
- [ ] Slot Agent 能获取页面快照和截图
- [ ] Slot Agent 能点击和输入
- [ ] Slot Agent 能检测 JS 错误
- [ ] Agent 身份支持浏览器 specialty
- [ ] MCP 协议可暴露浏览器工具
- [ ] E2E 测试可自动运行
- [ ] 同步到 4 个节点正常工作

## 不要做
- 不修改 dispatch.py 核心调度逻辑
- 不修改 guardian.py
- 不改动现有的 task-watcher
