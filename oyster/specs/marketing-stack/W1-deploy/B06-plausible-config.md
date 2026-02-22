---
task_id: B06-plausible-config
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: ["B05-plausible-deploy"]
modifies: ["~/.oyster-keys/plausible/sites.json"]
executor: glm
---

## 目标
Configure Plausible with 9 product domains as sites and generate shared links for embedding

## 约束
- Add 9 sites: clawmarketing.com, clawphones.com, worldglasses.com, gem.oyster-labs.com, clawvision.com, clawglasses.com, getpuffy.com, oysterrepublic.com, agentforge.dev
- Generate shared link for each site (public stats access)
- Timezone: America/Los_Angeles
- Save config to ~/.oyster-keys/plausible/sites.json
- JSON format: {"domain": {"shared_link": "...", "site_id": "..."}}

## 验收标准
- [ ] 9 sites registered in Plausible UI
- [ ] Shared link generated for each site
- [ ] Links saved to ~/.oyster-keys/plausible/sites.json
- [ ] Test shared link access: curl shared_link returns stats page
- [ ] JavaScript snippet URL available for each site
- [ ] All sites show "Awaiting first pageview" status

## 不要做
- 不要安装 Plausible script (产品 repo 负责)
- 不要配置 goals/funnels (后续)
- 不要设置 email reports
- 不要修改 docker-compose
