# Oyster Labs 基础设施使用指南

## 已部署服务

| 服务 | 地址 | 用途 |
|------|------|------|
| **n8n** | http://localhost:5678 | 工作流自动化 |
| **LocalAI** | http://localhost:8080 | 本地 LLM 推理 |
| **Netdata** | http://localhost:19999 | 实时监控 |

---

## 1. SOPS 密钥管理

### 快速开始

```bash
# 1. 解密文件
cd ~/Downloads/infrastructure
SOPS_AGE_KEY_FILE=~/.sops/agekeys.txt sops decrypt secrets.env.encrypted

# 2. 编辑加密文件（自动解密→编辑→自动加密）
SOPS_AGE_KEY_FILE=~/.sops/agekeys.txt sops edit secrets.env.encrypted

# 3. 加密新文件
SOPS_AGE_KEY_FILE=~/.sops/agekeys.txt sops encrypt plain.env --output secrets.env.encrypted
```

### 工作原理

```
原始文件                     加密后
┌─────────────┐          ┌─────────────────────┐
│ DATABASE_URL│          │ ENC[AES256_GCM,data:│
│ =postgresql │   ──►    │ LgBEJYdptarszuBow... │
│ ...        │          │ ...                 │
└─────────────┘          └─────────────────────┘
```

### 在 Git 中使用

```bash
# .gitignore 添加
*.env              # 原始文件不提交
!*.env.encrypted   # 加密文件可以提交

# 团队共享：把公钥加入 .sops.yaml
creation_rules:
  - age: >-
      age1eqmr908nfnn7p5qly0r2a4v89w3z046vvk6cccdcy69zkvk9nqvsejm3cp  # Howard
      age1xxxxx...  # 队友的公钥
```

---

## 2. n8n 工作流自动化

### 访问
- 地址: http://localhost:5678
- 首次打开需要设置账号

### 快速示例：定时任务

1. 打开 n8n → New Workflow
2. 添加节点：**Schedule Trigger** → 每小时/每天
3. 添加节点：**HTTP Request** → 调用 API
4. 添加节点：**Slack/Discord** → 发送通知

### AI 工作流示例

```javascript
// n8n 中的 AI 节点
{
  "model": "openai",
  "prompt": "分析今天销售数据",
  "temperature": 0.7
}
```

### 常用集成

| 集成 | 用途 |
|------|------|
| HTTP Request | 任意 API |
| GitHub | 代码提交/Issue |
| Slack/Discord | 通知 |
| Gmail/Email | 邮件 |
| Webhook | 接收外部请求 |
| OpenAI/Anthropic | AI 对话 |
| **MCP** | 调用外部工具 |

---

## 3. LocalAI 本地 LLM

### API 调用

```bash
# 测试 API
curl http://localhost:8080/v1/models

# 调用聊天
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:1b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 支持的模型

```bash
# 查看可用模型
curl http://localhost:8080/v1/models

# 下载模型
curl http://localhost:8080/models/install \
  -d '{"url": "llama3.2:1b"}'
```

### 与 n8n 集成

```
n8n → HTTP Request → LocalAI
URL: http://host.docker.internal:8080/v1/chat/completions
```

---

## 4. Netdata 监控

### 访问
- 地址: http://localhost:19999

### 监控指标

| 面板 | 内容 |
|------|------|
| System | CPU/内存/磁盘/网络 |
| Applications | 容器/进程 |
| Web Servers | Nginx/Apache |
| Databases | MySQL/PostgreSQL/Redis |
| Containers | Docker/K8s |

### 告警配置

```yaml
# /etc/netdata/health.d/cpu.conf
alarm: cpu_usage
lookup: average -60s unaligned
warn: $this > 80%
crit: $this > 95%
```

---

## 5. Docker 管理

```bash
# 查看状态
docker ps

# 查看日志
docker logs oyster-n8n
docker logs oyster-localai
docker logs oyster-netdata

# 重启服务
docker restart oyster-n8n
docker restart oyster-localai
docker restart oyster-netdata

# 停止全部
cd ~/Downloads/infrastructure && docker-compose down
```

---

## 6. MCP 集成（进阶）

### 什么是 MCP？

MCP (Model Context Protocol) 让 AI 可以调用外部工具

```
AI Agent ──► MCP Server ──► 本地服务/API
         ──► n8n
         ──► LocalAI
         ──► Netdata
```

### 配置示例

```json
{
  "mcpServers": {
    "n8n": {
      "command": "npx",
      "args": ["-y", "@n8n/mcp-server"],
      "env": {
        "N8N_API_KEY": "your-api-key",
        "N8N_URL": "http://localhost:5678"
      }
    }
  }
}
```

---

## 快速检查清单

```bash
# 检查所有服务状态
docker ps | grep oyster

# 检查端口
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678  # n8n
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080  # LocalAI
curl -s -o /dev/null -w "%{http_code}" http://localhost:19999 # Netdata
```

---

## 下一步建议

1. **SOPS**: 把现有的 `.env` 文件加密
2. **n8n**: 创建一个简单的自动化工作流（如定时检查网站）
3. **LocalAI**: 下载一个轻量模型测试
4. **Netdata**: 看看本机的实时监控数据
