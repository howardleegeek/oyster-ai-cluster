---
task_id: S05-linkedin-message
project: linkedin-connect
priority: 5
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化消息发送逻辑，确保能正确填写自定义消息

## 具体改动
改进 `send_message` 方法：

```python
def send_message(self, name: str):
    """发送带消息的邀请"""
    try:
        # 等待对话框出现
        time.sleep(1)
        
        # 查找消息输入框 - 多种选择器
        textarea_selectors = [
            'textarea[name="message"]',
            'textarea#custom-message',
            'textarea[placeholder*="message"]',
            'div[contenteditable="true"]',
        ]
        
        textarea = None
        for selector in textarea_selectors:
            textarea = self.page.query_selector(selector)
            if textarea:
                break
        
        if textarea:
            # 替换 {first_name} 变量
            message = self.args.message.format(first_name=name)
            textarea.fill(message)
            time.sleep(0.5)
        
        # 点击发送按钮
        send_selectors = [
            'button[aria-label*="Send"]',
            'button:has-text("Send")',
            'button:has-text("发送")',
        ]
        
        for selector in send_selectors:
            send_btn = self.page.query_selector(selector)
            if send_btn and send_btn.is_visible():
                send_btn.click()
                time.sleep(1)
                break
                
    except Exception as e:
        self.logger.log(f"Message send error: {e}")
```

## 验收标准
- [ ] 消息能正确填写
- [ ] 发送按钮能正确点击
