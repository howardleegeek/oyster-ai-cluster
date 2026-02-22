---
task_id: S02-do-a-focused-hardening-pass-d
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
do a focused hardening pass: define canonical runtime paths, exclude/archive dup


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
