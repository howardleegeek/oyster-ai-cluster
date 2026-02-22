---
task_id: S30-cicd
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
CI/CD Pipeline - GitHub Actions自动化

##具体改动
1. 创建 .github/workflows/ci.yml - 持续集成
2. 创建 .github/workflows/deploy.yml - 部署
3. 添加 Dockerfile
4. 添加 docker-compose.yml

##验收标准
- [ ] CI workflow可运行
- [ ] 自动运行测试
- [ ] Docker镜像可构建
