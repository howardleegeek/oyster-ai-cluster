---
task_id: S106-ship-guardrails
project: gem-platform
priority: 2
depends_on:
  - S103-ci-security-hygiene
modifies:
  - scripts/ship_check.sh
  - SHIP_GUARDRAILS.md
  - .github/workflows/ci.yml
executor: glm
---

## Goal
Add explicit guardrails so we never accidentally merge/collect a broken build to `main`.

This is a safety layer on top of dispatch+DAG:
- a single, canonical verification script (`scripts/ship_check.sh`)
- documented “merge/collect gate” procedure (`SHIP_GUARDRAILS.md`)
- CI wired to the same script so local == CI

## Constraints
- No new paid tools.
- No secrets committed.
- Keep CI runtime reasonable (split backend/frontend checks by job).
- Do not modify dispatch infrastructure code.

## Required Changes
### 1) Add `scripts/ship_check.sh`
- Bash script with `set -euo pipefail`.
- Supports subcommands:
  - `hygiene`: fail if repo tracks forbidden files (`.env`, `*.pem`, `*.key`, `._*`, etc.).
  - `backend`: `cd backend` then run `python -m compileall -q app` and `pytest -q`.
  - `frontend`: `cd lumina` then run `npm ci`, `npm run build`, `npx tsc --noEmit`.
  - `all`: runs `hygiene + backend + frontend`.

### 2) Add `SHIP_GUARDRAILS.md`
Document the exact “merge/collect gate” protocol:
- Only run `collect` after `S105` PASS.
- Always run `dispatch report gem-platform` first; if any FAIL, write fix specs and re-run.
- After collect (on an integration branch), run `./scripts/ship_check.sh all`.

### 3) Wire CI to the script
Update `.github/workflows/ci.yml` so:
- backend job runs `./scripts/ship_check.sh hygiene` and `./scripts/ship_check.sh backend`
- frontend job runs `./scripts/ship_check.sh hygiene` and `./scripts/ship_check.sh frontend`
- Remove any `|| true` so failures actually fail CI.

## Acceptance Criteria
- `scripts/ship_check.sh` exists and works for all subcommands.
- CI uses the script and fails correctly on errors.
- No secrets or `.env` are newly tracked.

## Do Not Do
- Do not add heavyweight security scanners as new dependencies.
- Do not change product logic; this is guardrail-only.
