---
task_id: S018-twenty-config
project: marketing-stack
priority: 1
estimated_minutes: 20
depends_on: ["S017-twenty-deploy"]
modifies: ["~/.oyster-keys/twenty/api-key.txt"]
executor: glm
---

## 目标
Configure Twenty CRM with sales pipeline, custom fields, and API key for automation

## 约束
- Pipeline stages: Lead → MQL (Marketing Qualified) → SQL (Sales Qualified) → Customer
- Custom fields on Person object: product_interest (select), source_platform (text), engagement_score (number)
- product_interest options: ClawMarketing, ClawPhones, WorldGlasses, GEM, getPuffy, OysterRepublic
- Generate API key with full access
- Save API key to ~/.oyster-keys/twenty/api-key.txt
- Workspace name: Oyster Labs Marketing

## 验收标准
- [ ] Workspace created and configured
- [ ] 4-stage pipeline created: Lead/MQL/SQL/Customer
- [ ] 3 custom fields added to Person object
- [ ] product_interest dropdown has 6 options
- [ ] API key generated and saved
- [ ] Test API call succeeds: curl -H "Authorization: Bearer <key>" http://.../api/graphql
- [ ] Pipeline visible in Opportunities view

## 不要做
- 不要导入 contacts/companies
- 不要创建 automation workflows
- 不要配置 email templates
- 不要修改 docker-compose
