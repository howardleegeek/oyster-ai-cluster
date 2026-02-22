---
task_id: S05-notification-system
project: clawphones-backend
priority: 2
depends_on: []
modifies:
  - ~/Downloads/clawphones-backend/app/plugins/email.py
  - ~/Downloads/clawphones-backend/app/notification/
executor: glm
---

## 目标
集成用户通知系统，使用 INFRA plugins.email (Resend)

## 约束
- 使用 backend 内置的 plugins.email
- 不修改现有移动端代码

## 具体改动

### 1. 配置 plugins.email
编辑 ~/Downloads/clawphones-backend/app/plugins/email.py:
```python
settings = {
    "enabled": True,
    "api_key": os.getenv("RESEND_API_KEY"),
    "from_email": "ClawPhones <noreply@clawphones.com>",
    "from_name": "ClawPhones",
}
```

### 2. 创建 Notification 模块
创建 app/notification/:
- app/notification/__init__.py
- app/notification/notification_router.py:
  - POST /v1/user/push-token - 注册推送 token
  - POST /v1/notification/send - 发送通知
  - GET /v1/notification/history - 通知历史
- app/notification/notification_service.py:
  - send_email_notification() - 邮件通知
  - send_sms_notification() - 短信通知
  - send_push_notification() - 推送通知

### 3. 通知模板
```python
NOTIFICATION_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to ClawPhones!",
        "template": "Welcome {name}, ..."
    },
    "task_completed": {
        "subject": "Task Completed!",
        "template": "Your task ..."
    },
    "payment_received": {
        "subject": "Payment Received",
        "template": "You received ..."
    },
    "alert": {
        "subject": "ClawVision Alert",
        "template": "Motion detected at ..."
    }
}
```

### 4. 配置环境变量
```
RESEND_API_KEY=re_xxx
```

### 5. 可选: SMS 插件
如果需要短信通知:
```python
# plugins/sms.py
settings = {
    "enabled": True,
    "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
    "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
    "from_number": os.getenv("TWILIO_FROM_NUMBER"),
}
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM_NUMBER=+1234567890
```

## 验收标准
- [ ] Email 插件配置正确
- [ ] /v1/notification/send 端点可用
- [ ] 邮件发送功能正常 (可 mock 测试)
- [ ] 测试通过

## 不要做
- 不改 iOS/Android 客户端代码
