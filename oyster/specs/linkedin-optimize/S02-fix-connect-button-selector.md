---
task_id: S02-linkedin-connect-btn
project: linkedin-connect
priority: 2
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
修复 Connect 按钮的 selector，确保能正确找到可点击的 Connect 按钮

## 具体改动
更新 `find_connect_btn` 方法，使用更健壮的 selector 策略：

```python
def find_connect_btn(self, result):
    """查找 Connect 按钮 - 多种策略"""
    # 策略 1: 直接查找包含 "Connect" 文本的按钮
    buttons = result.query_selector_all("button")
    
    for btn in buttons:
        btn_text = btn.inner_text().strip().lower()
        # 跳过 Pending 和 Message 按钮
        if "connect" in btn_text and "pending" not in btn_text and "message" not in btn_text:
            # 检查按钮是否可见和可用
            if btn.is_visible() and btn.is_enabled():
                return btn
    
    # 策略 2: 查找 svg 图标 + Connect 文本的组合
    # LinkedIn 有时候用 icon + text
    return None
```

## 验收标准
- [ ] dry-run 能识别 Connect 按钮
- [ ] 跳过已 Pending 的连接
