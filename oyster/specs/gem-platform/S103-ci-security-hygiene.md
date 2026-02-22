---
task_id: S103-ci-security-hygiene
project: gem-platform
priority: 2
depends_on: []
modifies:
  - .github/workflows/ci.yml
  - .gitignore
  - backend/.env
  - lumina/.env
  - backend/app/**/._*.py
executor: glm
---

## Goal
Make the repo safe and CI-enforced for a real production push:

- No tracked secrets (.env) in git
- No OS metadata / AppleDouble files (`._*`) committed
- CI fails on test/type failures (remove `|| true`)

## Constraints
- Do not add new paid tooling.
- Keep CI simple.

## Required Changes
- Ensure `.env` files are not tracked and are gitignored. Keep `.env.example`.
- Remove stray `._*` files from the repository and add ignore rules.
- Fix CI workflow so it is strict:
  - Backend:
    - use `python -m compileall -q app` instead of shell glob patterns
    - run pytest without ignoring failures
  - Frontend:
    - run `npm run build`
    - run `npx tsc --noEmit` and fail if it fails

## Acceptance Criteria
- GitHub Actions workflow passes on main branch.
