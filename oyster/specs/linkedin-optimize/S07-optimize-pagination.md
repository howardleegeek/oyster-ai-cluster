---
task_id: S07-linkedin-pagination
project: linkedin-connect
priority: 7
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化翻页逻辑，确保能正确翻到下一页

## 具体改动
改进 `go_next_page` 方法：

```python
def go_next_page(self) -> bool:
    """翻到下一页"""
    try:
        # 多种翻页按钮选择器
        next_selectors = [
            'button[aria-label="Next"]',
            'button:has-text("Next")',
            'button[aria-label="next"]',
            'a[href*="page"]',
        ]
        
        for selector in next_selectors:
            next_btn = self.page.query_selector(selector)
            if next_btn and next_btn.is_enabled() and next_btn.is_visible():
                next_btn.click()
                time.sleep(2)
                self.page.wait_for_load_state("networkidle")
                return True
        
        return False
    except Exception as e:
        self.logger.log(f"Next page error: {e}")
        return False
```

## 验收标准
- [ ] 能正确翻页
