---
task_id: S35-cicd-github-actions
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加GitHub Actions CI/CD

##具体改动
1. 创建 .github/workflows/ci.yml - 持续集成
2. 创建 .github/workflows/deploy.yml - 部署
3. 完善 Dockerfile
4. 添加 docker-compose.prod.yml

##验收标准
- [ ] CI workflow可运行
- [ ] 自动运行pytest
- [ ] Docker镜像可构建
