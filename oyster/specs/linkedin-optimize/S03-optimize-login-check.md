---
task_id: S03-linkedin-login-check
project: linkedin-connect
priority: 3
depends_on: []
modifies:
  - backend/scripts/linkedin_cdp.py
executor: glm
---

## 目标
优化登录检测逻辑，更准确地判断 LinkedIn 是否已登录

## 具体改动
改进 `check_login` 方法，增加多种检测方式：

```python
def check_login(self) -> bool:
    """检查是否已登录"""
    try:
        self.page.goto("https://www.linkedin.com/feed", timeout=10000)
        time.sleep(2)
        
        # 方法 1: 检查是否有登录按钮
        login_btn = self.page.query_selector('a[href*="login"], button[href*="login"]')
        if login_btn:
            return False
        
        # 方法 2: 检查是否有 feed 元素
        feed = self.page.query_selector('.feed-shared-update-v2, .scaffold-finite-scroll, main[aria-label="Feed"]')
        if feed:
            return True
            
        # 方法 3: 检查 URL 是否重定向到 feed
        if "feed" in self.page.url:
            return True
            
        return False
    except Exception as e:
        self.logger.log(f"Login check error: {e}")
        return False
```

## 验收标准
- [ ] 登录成功时正确返回 True
- [ ] 未登录时正确返回 False
