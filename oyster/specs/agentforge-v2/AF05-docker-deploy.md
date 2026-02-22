---
task_id: AF05-docker-deploy
project: agentforge-v2
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["docker/", "Dockerfile", "docker-compose.yml"]
executor: glm
---
## 目标
更新 Docker 配置支持一键部署 AgentForge

## 技术方案
1. 更新 Dockerfile：镜像名改为 agentforge
2. 更新 docker-compose.yml：
   - 添加 DISPATCH_CONTROLLER_URL 环境变量
   - 添加 DISPATCH_ENABLED 环境变量
   - 保留现有的数据库配置（SQLite/MySQL/Postgres）
3. 添加 docker-compose.prod.yml 生产配置
4. 添加 .env.example 文件

## 约束
- 基于现有 Docker 配置修改
- 支持 arm64 和 amd64
- 不改构建过程

## 验收标准
- [ ] docker build -t agentforge . 成功
- [ ] docker-compose up 可以启动
- [ ] .env.example 包含所有环境变量说明
- [ ] DISPATCH_CONTROLLER_URL 在 .env.example 中有文档

## 不要做
- 不改 node.js 构建配置
- 不加新的系统依赖
