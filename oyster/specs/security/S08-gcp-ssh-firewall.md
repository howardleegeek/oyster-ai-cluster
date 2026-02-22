---
task_id: GW-004
project: security
priority: P1
depends_on: ["GW-001", "GW-002", "GW-003"]
modifies: ["GCP firewall rules"]
executor: glm
---

## 目标
限制 GCP SSH 防火墙仅允许可信 IP 访问，关闭 0.0.0.0/0

## 步骤
1. 获取当前 IP：`curl -s ifconfig.me`
2. 列出现有防火墙规则：`gcloud compute firewall-rules list --filter="allowed[].ports:22"`
3. 记录要删除/修改的规则名称
4. 创建受限规则：
   ```bash
   gcloud compute firewall-rules create allow-ssh-trusted \
     --direction=INGRESS --priority=1000 --network=default \
     --action=ALLOW --rules=tcp:22 \
     --source-ranges=<CURRENT_IP>/32 \
     --description="SSH restricted to trusted IPs"
   ```
5. 删除全开放规则（确认名称后）
6. 验证：从其他 IP 无法 SSH

## 验收标准
- [ ] `gcloud compute firewall-rules list` 无 0.0.0.0/0 的 22 端口规则
- [ ] 从可信 IP 可以 SSH
- [ ] 从其他 IP 连接超时

## 回滚
```bash
gcloud compute firewall-rules create allow-ssh-all \
  --direction=INGRESS --action=ALLOW --rules=tcp:22 \
  --source-ranges=0.0.0.0/0
```

## 不要做
- 不删除非 SSH 的防火墙规则
- 不修改 VPC 网络配置
