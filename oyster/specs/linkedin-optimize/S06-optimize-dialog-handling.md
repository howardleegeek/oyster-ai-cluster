---
task_id: S06-linkedin-dialog
project: linkedin-connect
priority: 6
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化对话框处理，处理 "How do you know X?" 弹窗

## 具体改动
改进 `handle_dialog` 方法：

```python
def handle_dialog(self):
    """处理连接对话框"""
    try:
        # 等待对话框出现
        time.sleep(1)
        
        # 检查是否有对话框
        dialog_selectors = [
            'div[role="dialog"]',
            'div.send-invite__outer',
            'div[aria-modal="true"]',
        ]
        
        dialog = None
        for selector in dialog_selectors:
            dialog = self.page.query_selector(selector)
            if dialog:
                break
        
        if not dialog:
            return
            
        # 查找 "Other" 选项
        other_selectors = [
            'button:has-text("Other")',
            'button[aria-label*="Other"]',
            'button:has-text("I don't know")',
        ]
        
        for selector in other_selectors:
            other_btn = self.page.query_selector(selector)
            if other_btn and other_btn.is_visible():
                other_btn.click()
                time.sleep(0.5)
                break
                
    except Exception as e:
        self.logger.log(f"Dialog handle error: {e}")
```

## 验收标准
- [ ] 能正确处理 "How do you know" 对话框
