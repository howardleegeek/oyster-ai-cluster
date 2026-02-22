---
task_id: GW-008
project: security
priority: P1
depends_on: ["GW-004"]
modifies: ["GCP nodes"]
executor: glm
---

## 目标
在所有 GCP/OCI 节点安装 fail2ban 防 SSH 暴力破解

## 步骤
在每个远程节点执行：
1. 安装：`sudo apt-get install -y fail2ban`
2. 创建配置 `/etc/fail2ban/jail.local`：
   ```ini
   [sshd]
   enabled = true
   port = 22
   filter = sshd
   logpath = /var/log/auth.log
   maxretry = 3
   bantime = 3600
   findtime = 600
   ```
3. 启动：`sudo systemctl enable fail2ban && sudo systemctl start fail2ban`
4. 验证：`sudo fail2ban-client status sshd`

目标节点：codex-node-1, glm-node-2, glm-node-3, glm-node-4, oci-arm-1, oci-micro-1, oci-micro-2

## 验收标准
- [ ] 所有节点 `fail2ban-client status sshd` 显示 active
- [ ] 3 次失败登录后 IP 被 ban

## 回滚
```bash
sudo systemctl stop fail2ban
sudo apt-get remove fail2ban
```

## 不要做
- 不修改 sshd_config
- 不重启 SSH 服务
