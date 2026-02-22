---
task_id: S17-device-monitoring
project: clawphones
priority: 2
depends_on: ["S18-batch-operations"]
modifies:
  - server.js
executor: glm
---

## 目标
实现设备监控告警功能

## 约束
- 不改 iOS/Android 代码
- 使用现有监控基础设施

## 具体改动
1. 添加设备在线状态监控
2. 实现心跳检测
3. 添加电量告警阈值
4. 添加存储空间告警
5. 写集成测试

## 验收标准
- [ ] 设备离线告警触发
- [ ] 电量 < 20% 告警
- [ ] 存储 < 10% 告警
- [ ] 测试通过

## 不要做
- 不改移动端代码
- 不加新依赖
