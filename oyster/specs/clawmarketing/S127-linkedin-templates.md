---
task_id: S127-linkedin-templates
project: clawmarketing
priority: 2
depends_on: []
modifies: ["backend/services/message_template.py"]
executor: glm
---
## 目标
实现消息模板系统，支持连接请求和 follow-up 变量替换

## 约束
- 支持 {{first_name}}, {{company}}, {{title}} 变量
- 预置 3 种连接请求模板 + 2 种 follow-up 模板
- 模板支持多语言
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_message_template.py 全绿
- [ ] MessageTemplate.render() 正确替换变量
- [ ] 内置模板可启用/禁用
- [ ] 支持自定义模板添加

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
