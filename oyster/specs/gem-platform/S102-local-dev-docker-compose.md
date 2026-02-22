---
task_id: S102-local-dev-docker-compose
project: gem-platform
priority: 2
depends_on: []
modifies:
  - docker-compose.yml
  - backend/.env.example
  - lumina/.env.example
  - backend/README.md
executor: glm
---

## Goal
One-command local dev that actually works:

- `docker compose up --build` brings up MySQL + Redis + backend
- Host can hit backend health endpoint at `http://localhost:8000/health`
- Frontend `.env.example` points to the correct backend base URL

## Constraints
- No new infra services.
- Keep configuration via environment variables.
- No secrets committed.

## Required Fixes
- Align `docker-compose.yml` with how the backend reads config:
  - ensure DB host points to `db` service
  - ensure Redis host points to `redis` service
  - ensure the container listens on the same port that is exposed/mapped
- Align backend env var names:
  - backend settings use `APP_SECRET` (not legacy `SECRET`)
  - update `backend/.env.example` accordingly

## Acceptance Criteria
- `docker compose up -d --build`
- `curl -sf http://localhost:8000/health | head -c 200`
- `docker compose down -v`
