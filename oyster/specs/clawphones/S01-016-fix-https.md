---
task_id: S01-016
project: clawphones
priority: 1
depends_on: ["S01-015"]
modifies: ["proxy/server.py", "ios/ClawPhones", "android/clawphones-android"]
executor: glm
---

## 目标
修复已知问题：HTTPS 配置

## 约束
- 后端 + iOS + Android
- 生产环境配置

## 具体改动
- 修改 proxy/server.py 添加 HTTPS 支持
- 修改 ios/ClawPhones/Services/DeviceConfig.swift
- 修改 android/clawphones-android/...

## 验收标准
- [ ] HTTPS 端点测试通过
- [ ] 客户端正确处理 HTTPS
