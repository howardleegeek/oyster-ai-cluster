---
task_id: G03-directus-deploy
project: marketing-stack
priority: 3
estimated_minutes: 30
depends_on: []
modifies: ["oyster/infra/docker-compose-marketing.yml", "oyster/infra/directus-schema/"]
executor: glm
---
## 目标
Deploy Directus headless CMS via Docker with PostgreSQL on port 8055, schema for products/content/assets/campaigns

## 约束
- PostgreSQL 15+ backend
- Directus latest stable version
- Schema: products, content, assets, campaigns tables
- Persist /opt/directus volume
- Admin credentials in ~/.oyster-keys/
- Internal network only

## 验收标准
- [ ] Directus accessible at http://localhost:8055
- [ ] PostgreSQL database initialized
- [ ] All 4 tables created with proper relations
- [ ] Admin login works
- [ ] docker-compose up -d starts successfully
- [ ] Schema definition exported to directus-schema/schema.json

## 不要做
- No public port exposure
- No sample data yet
- No custom extensions
