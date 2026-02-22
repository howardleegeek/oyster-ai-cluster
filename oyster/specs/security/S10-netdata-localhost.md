---
task_id: GW-006
project: security
priority: P1
depends_on: []
modifies: ["docker-compose.yml"]
executor: glm
---

## 目标
将 Netdata 绑定到 localhost，防止系统信息泄露

## 步骤
1. 找到 Netdata 的 docker-compose.yml 配置
2. 修改 ports 为 `"127.0.0.1:19999:19999"`
3. 重启：`docker-compose up -d netdata`
4. 验证：`ss -tlnp | grep 19999` 应显示 127.0.0.1

## 验收标准
- [ ] Netdata 仅监听 127.0.0.1:19999
- [ ] 外部 IP 无法访问 19999 端口

## 回滚
改回 `"19999:19999"` 并重启

## 不要做
- 不卸载 Netdata
- 不修改监控配置
