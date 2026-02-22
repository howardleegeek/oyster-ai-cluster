---
task_id: S012-posthog-config
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["S011-posthog-deploy"]
modifies: ["~/.oyster-keys/posthog/project-keys.json"]
executor: glm
---

## 目标
Configure PostHog with 9 product projects and generate API keys for each

## 约束
- Create 9 projects: ClawMarketing, ClawPhones, WorldGlasses, GEM, ClawVision, ClawGlasses, getPuffy, OysterRepublic, AgentForge
- Generate project API key + personal API token per project
- Save keys to ~/.oyster-keys/posthog/project-keys.json (JSON format)
- Enable features: session recording, feature flags, cohorts
- Set timezone: America/Los_Angeles
- Organization name: Oyster Labs

## 验收标准
- [ ] 9 projects created in PostHog UI
- [ ] Each project has unique API key
- [ ] Personal API token generated with full access
- [ ] Keys saved to ~/.oyster-keys/posthog/project-keys.json
- [ ] JSON format: {"project_name": {"api_key": "...", "token": "..."}}
- [ ] Test API call succeeds for each project
- [ ] Session recording enabled for all projects

## 不要做
- 不要安装 PostHog snippet (产品 repo 负责)
- 不要配置 data retention limits
- 不要创建 custom events (产品定义)
- 不要修改 docker-compose
