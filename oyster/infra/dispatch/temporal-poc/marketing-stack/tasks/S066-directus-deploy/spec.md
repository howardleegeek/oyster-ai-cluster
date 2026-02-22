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

## FALLBACK PROTOCOL INITIATED
Previous attempts continuously failed. Final error:
```
Activity cancelled
```

**CRITICAL INSTRUCTION**: Abandon your previous approach. Simplify your solution, use alternative methods, or stub the functionality safely. Do NOT repeat the same mistakes.