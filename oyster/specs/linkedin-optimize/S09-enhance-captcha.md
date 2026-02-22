---
task_id: S09-linkedin-captcha
project: linkedin-connect
priority: 9
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
增强 CAPTCHA 检测和处理

## 具体改动
改进 `check_captcha` 方法并添加自动处理：

```python
def check_captcha(self) -> bool:
    """检测 CAPTCHA"""
    try:
        page_text = self.page.content().lower()
        
        captcha_indicators = [
            "captcha",
            "verify you're human",
            "security check",
            "验证",
            "请验证",
            "robot",
            "unusual activity",
        ]
        
        detected = [ind for ind in captcha_indicators if ind in page_text]
        
        # 检查 CAPTCHA 表单
        captcha_form = self.page.query_selector('form[captcha], input[name*="captcha"]')
        
        return len(detected) > 0 or captcha_form is not None
        
    except:
        return False
```

在处理循环中添加 CAPTCHA 暂停：

```python
if self.check_captcha():
    self.logger.log("CAPTCHA detected! Pausing for manual intervention...")
    print("⚠️  CAPTCHA detected! Please solve it manually, then press Enter...")
    input()
```

## 验收标准
- [ ] 能检测 CAPTCHA
- [ ] 自动暂停等待用户处理
