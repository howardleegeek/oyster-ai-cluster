# Marketing Stack Waves 3-4-5 Spec Index

Total: 67 atomic spec files

## Wave 3-A: Advanced Tool Deploy (8 specs)
**Location**: `W3-tools/`

1. G01-mautic-deploy.md - Deploy Mautic marketing automation
2. G02-mautic-campaigns.md - Configure 4 email campaigns
3. G03-directus-deploy.md - Deploy Directus CMS + PostgreSQL
4. G04-directus-workflow.md - Configure editorial workflow + webhooks
5. G05-grapesjs-integrate.md - Integrate GrapesJS page builder
6. G06-grapesjs-templates.md - Create 3 landing page templates
7. G07-obsei-deploy.md - Deploy social listening (Twitter/Reddit)
8. G08-alwrity-deploy.md - Deploy AI content generation

## Wave 3-B: New Modules (4 specs)
**Location**: `W3-modules/`

1. H01-competitor-tracker.md - Competitor tracking module
2. H02-ab-testing.md - A/B testing engine
3. H03-trending-enhance.md - Cross-platform trend aggregation
4. H04-main-cli-commands.md - Add CLI commands (campaign, analytics, competitor, test)

## Wave 4: Product Rollout (45 specs)
**Location**: `W4-rollout/`

9 products × 5 tasks each:

### Products:
1. **ClawMarketing (cm)** - Marketing automation platform
2. **ClawPhones (cp)** - Custom phone cases
3. **WorldGlasses (wg)** - AR smart glasses
4. **GEM (gem)** - AI agents platform
5. **ClawVision (cv)** - Computer vision API
6. **ClawGlasses (cg)** - Custom eyeglasses
7. **getPuffy (pf)** - Premium jackets
8. **OysterRepublic (or)** - Digital nation/Web3
9. **AgentForge (af)** - AI agent framework

### 5 Tasks per Product:
1. **-1-analytics.md** - Install PostHog + Plausible tracking
2. **-2-seo.md** - Set up SerpBear keyword tracking (50 keywords)
3. **-3-content.md** - Create initial 5-post social campaign
4. **-4-email.md** - Create email signup + Listmonk integration
5. **-5-calendar.md** - Create 2-week social calendar (30+ posts)

**File naming**: `I-{product_code}-{task_number}-{task_name}.md`

## Wave 5: E2E Testing (10 specs)
**Location**: `W5-test/`

1. J01-test-content-pipeline.md - Pomelli → n8n → Postiz → analytics
2. J02-test-email-pipeline.md - Content → Listmonk → PostHog tracking
3. J03-test-crm-pipeline.md - PostHog event → n8n → Twenty CRM
4. J04-test-seo-pipeline.md - SerpBear rank drop → alert → refresh
5. J05-test-listening-pipeline.md - Obsei mention → alert → response draft
6. J06-test-data-consistency.md - Cross-reference metrics (PostHog/Plausible/dashboard)
7. J07-test-fallback.md - Test n8n/PostHog/LLM fallback paths
8. J08-test-security.md - API keys, network, ports, rate limiting audit
9. J09-test-performance.md - Benchmark n8n/PostHog/content/queue
10. J10-test-runbook.md - Write ops runbook (restart, backup, alerts, troubleshooting)

## Execution Order

1. **Wave 3-A** (G01-G08): Deploy advanced tools - parallel execution OK
2. **Wave 3-B** (H01-H04): Build new modules - depends on Wave 1-2 + 3-A
3. **Wave 4** (I-*): Product rollout - can run in parallel per product
4. **Wave 5** (J01-J10): E2E testing - sequential, after Waves 3-4 complete

## Dependencies

- Wave 3-A depends on: Wave 1-2 infrastructure (n8n, Docker, unified DB)
- Wave 3-B depends on: Wave 1-2 + Wave 3-A (G07, B12, A01, etc.)
- Wave 4 depends on: Wave 1-2 (A02, B04, B06, B08, B12, D01, D02)
- Wave 5 depends on: All previous waves complete

## Dispatch Command

```bash
# Start all Wave 3-4-5 specs
python3 ~/Downloads/oyster/infra/dispatch/dispatch.py start marketing-stack

# Check status
python3 ~/Downloads/oyster/infra/dispatch/dispatch.py status marketing-stack

# Collect results
python3 ~/Downloads/oyster/infra/dispatch/dispatch.py collect marketing-stack

# Generate report
python3 ~/Downloads/oyster/infra/dispatch/dispatch.py report marketing-stack
```

## Estimated Timeline

- **Wave 3-A**: 8 specs × 25-30 min = ~4 hours (parallel: 30 min)
- **Wave 3-B**: 4 specs × 25-30 min = ~2 hours (parallel: 30 min)
- **Wave 4**: 45 specs × 15-20 min = ~12 hours (parallel: 1-2 hours)
- **Wave 5**: 10 specs × 15-30 min = ~4 hours (sequential: 4 hours)

**Total sequential**: ~22 hours
**Total parallel (32 agents)**: ~6-8 hours

---

Generated: 2026-02-19
Format: Atomic spec (YAML frontmatter + markdown)
Executor: GLM (default)
