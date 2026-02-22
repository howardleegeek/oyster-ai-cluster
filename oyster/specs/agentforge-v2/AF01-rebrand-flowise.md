---
task_id: AF01-rebrand-flowise
project: agentforge-v2
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["packages/ui/src/", "package.json", "README.md", "docker/"]
executor: glm
---
## 目标
将 Flowise 品牌替换为 AgentForge 品牌（白标改造）

## 技术方案
1. 全局搜索替换 "Flowise" → "AgentForge", "flowise" → "agentforge"
2. 替换 logo 和 favicon（UI 包里的 src/assets/）
3. 更新 package.json 的 name/description/repository
4. 更新 docker-compose 和 Dockerfile 中的镜像名
5. 更新 README.md 为 AgentForge 介绍

## 约束
- 不改功能逻辑，只改品牌文字和资产
- 保留 Apache 2.0 LICENSE（只添加 "Based on Flowise" 声明）
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] `grep -ri "flowise"` 在关键代码文件中返回 0 结果（LICENSE 中允许保留）
- [ ] package.json name 改为 @oyster/agentforge
- [ ] Docker 镜像名改为 agentforge
- [ ] README 更新

## 不要做
- 不改业务逻辑
- 不改 UI 布局/CSS
- 不删 LICENSE
