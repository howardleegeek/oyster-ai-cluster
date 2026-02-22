---
task_id: S02-add-a-lightweight-release-gate
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
add a lightweight release gate now: required `typecheck + lint + targeted smoke 


## Identified Risks
- If discovery continues without hardening, iteration speed will drop as regressions increase from codebase sprawl.
- 0KB or placeholder infra/config files can create false confidence and environment-specific failures during deployment.
- Locking to one template too early may reduce learning if telemetry is weak; keep feature-flagged fallback until metrics are stable.


## Constraints
- Work within the existing codebase structure
- Write meaningful tests for new functionality
- Do not refactor unrelated code
- Do not change UI/CSS unless explicitly required

## Acceptance Criteria
- [ ] Core functionality implemented
- [ ] Tests pass
- [ ] No lint errors
- [ ] Changes are minimal and focused

## Do NOT
- Restructure the project layout
- Add unnecessary dependencies
- Over-engineer the solution


## Previous Attempt Failed
Exit code 1

Fix the issue above.