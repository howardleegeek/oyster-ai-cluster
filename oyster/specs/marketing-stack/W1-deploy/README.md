# Wave 1-B: Open-Source Tool Deployment Specs

**Total specs:** 12
**Total estimated time:** 285 minutes (~4.75 hours with 32 parallel agents)
**Target:** Deploy 6 marketing tools on GCP infrastructure

## Deployment Architecture

### Node Distribution
- **codex-node-1** (GCP): n8n, Listmonk, SerpBear
- **glm-node-2** (GCP): PostHog, Plausible, Twenty CRM

## Spec Breakdown

### n8n Workflow Automation
- **B01-n8n-deploy** (30 min): Docker deployment with postgres
- **B02-n8n-config** (20 min): SSL, admin, credential vault

### PostHog Analytics
- **B03-posthog-deploy** (30 min): Full stack deployment
- **B04-posthog-config** (20 min): 9 product projects + API keys

### Plausible Analytics
- **B05-plausible-deploy** (30 min): Privacy-focused analytics
- **B06-plausible-config** (15 min): 9 domains + shared links

### Listmonk Newsletter
- **B07-listmonk-deploy** (20 min): Email platform deployment
- **B08-listmonk-config** (20 min): SES + 6 lists + 4 templates

### Twenty CRM
- **B09-twenty-deploy** (30 min): CRM platform deployment
- **B10-twenty-config** (20 min): Pipeline + custom fields + API

### SerpBear SEO
- **B11-serpbear-deploy** (20 min): Rank tracking deployment
- **B12-serpbear-config** (30 min): 6 domains + 300 keywords + GSC

## Dependency Chain

```
B01 → B02 (n8n)
B03 → B04 (PostHog)
B05 → B06 (Plausible)
B07 → B08 (Listmonk)
B09 → B10 (Twenty)
B11 → B12 (SerpBear)
```

All 6 chains can run in parallel.

## Dispatch Command

```bash
python3 ~/Downloads/oyster/infra/dispatch/dispatch.py start marketing-stack
```

## Verification

After deployment, all tools should be accessible:
- n8n: http://codex-node-1:5678
- PostHog: http://glm-node-2:8000
- Plausible: http://glm-node-2:8100
- Listmonk: http://codex-node-1:9000
- Twenty: http://glm-node-2:3000
- SerpBear: http://codex-node-1:3001

## API Keys Storage

All credentials saved to `~/.oyster-keys/<tool>/`
