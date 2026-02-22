---
task_id: S01-linkedin-selector
project: linkedin-connect
priority: 1
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
修复 LinkedIn 搜索结果页名字提取的 selector

## 约束
- 只改 selector，不改核心逻辑
- 保持向后兼容

## 具体改动
更新 `linkedin_cdp.py` 中 `process_single_person` 方法的名字提取 selector：

当前代码（需要修复）：
```python
name_elem = result.query_selector("span.actor-name, div.entity-result__title-text a")
```

改为多种 selector 尝试：
```python
# 尝试多种可能的名字 selector
selectors = [
    "span.actor-name",
    "div.entity-result__title-text a",
    "div[data-test-id="profile-name"]",
    "span[aria-hidden='true'].mr1",
    "div .pv-top-card--list li:first-child",
    ".entity-result__title-text span",
    "span.t-16.t-black.t-normal",
    "span.a11y-focusable-element",
]
```

使用循环尝试每个 selector，找到第一个有效的。

## 验收标准
- [ ] 运行 dry-run，名字能正确显示（不是 Unknown）
- [ ] 验证命令：`python3 -m scripts.linkedin_cdp connect 9222 --search-url "..." --max 1 --dry-run`
