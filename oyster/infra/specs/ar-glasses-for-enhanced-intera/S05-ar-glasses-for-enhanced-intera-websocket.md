---
task_id: S05-ar-glasses-for-enhanced-intera-websocket
project: ar-glasses-for-enhanced-intera
priority: 2
depends_on: ["S01-ar-glasses-for-enhanced-intera-bootstrap"]
modifies: ["backend/main.py", "backend/websockets/interaction.py"]
executor: glm
---
## 目标
设置WebSocket连接以实现AR眼镜与后端的实时通信

## 约束
- 在bootstrap基础上添加功能
- 写测试
- 不留 TODO/FIXME

## 验收标准
- [ ] 功能实现完整
- [ ] pytest 能跑通
