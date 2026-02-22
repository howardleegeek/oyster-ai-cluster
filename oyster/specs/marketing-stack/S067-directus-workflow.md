---
task_id: S067-directus-workflow
project: marketing-stack
priority: 3
estimated_minutes: 25
depends_on: [S066-directus-deploy]
modifies: ["oyster/infra/directus-schema/workflows.json"]
executor: glm
---
## 目标
Configure Directus editorial workflow (draft→review→publish), asset library for Pomelli outputs, webhook to n8n on content events

## 约束
- Status field: draft, review, published
- Roles: editor (draft/review), publisher (publish)
- Asset library links to Pomelli output directory
- Webhooks on: content.items.create, content.items.update, content.items.publish
- Webhook target: http://localhost:5678/webhook/directus

## 验收标准
- [ ] Workflow statuses configured on content table
- [ ] Role permissions set correctly
- [ ] Asset library shows Pomelli outputs
- [ ] Webhooks fire on content events
- [ ] Test workflow: draft → review → publish
- [ ] n8n receives webhook (log verification)

## 不要做
- No complex approval chains yet
- No email notifications from Directus
- No custom fields beyond schema
