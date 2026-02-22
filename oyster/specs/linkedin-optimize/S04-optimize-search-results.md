---
task_id: S04-linkedin-search-results
project: linkedin-connect
priority: 4
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化搜索结果解析，更可靠地提取搜索结果列表

## 具体改动
改进 `process_results` 方法的结果选择器：

```python
def process_results(self):
    # 更可靠的结果选择器
    selectors = [
        "li.reusable-search__result-container",
        "li.artdeco-list__item",
        "div[data-test-id="search-results"] li",
        ".search-results__container li",
    ]
    
    for selector in selectors:
        results = self.page.query_selector_all(selector)
        if results and len(results) > 0:
            self.logger.log(f"Found {len(results)} results with selector: {selector}")
            return results
    
    return []
```

## 验收标准
- [ ] 能正确识别搜索结果数量
