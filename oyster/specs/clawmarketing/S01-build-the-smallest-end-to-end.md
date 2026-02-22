---
task_id: S01-build-the-smallest-end-to-end
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
build the smallest end-to-end experiment loop first: fixed benchmark set, run te


## Identified Risks
- Without hardening, rapid auto-merge velocity can create silent regressions and code drift across duplicate trees, reducing trust in discovery results.


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
