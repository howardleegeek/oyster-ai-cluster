---
task_id: S104-deployment-docs
project: gem-platform
priority: 3
depends_on:
  - S102-local-dev-docker-compose
  - S103-ci-security-hygiene
modifies:
  - DEPLOYMENT.md
  - backend/README.md
  - lumina/README.md
executor: glm
---

## Goal
Document a clean path to production deployment for both backend and frontend.

## Constraints
- No secrets committed.
- Keep docs actionable and copy/paste friendly.

## Required Content
- Local dev:
  - docker compose steps
  - required env vars
- Backend production:
  - recommended deployment target (Cloud Run) using the existing Dockerfile
  - required env vars (ENV, APP_SECRET, DB_HOST/DB_USER/DB_PASSWD/DB_NAME, REDIS_*, platform wallet address, SOL rpc URL)
- Frontend production:
  - Vercel deploy steps
  - required env vars (VITE_API_BASE_URL, Solana rpc if configurable)

## Acceptance Criteria
- `DEPLOYMENT.md` exists and is up to date.
