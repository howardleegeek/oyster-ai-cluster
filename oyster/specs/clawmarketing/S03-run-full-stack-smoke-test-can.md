---
task_id: S03-run-full-stack-smoke-test-can
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
run full stack smoke test: can user login → create campaign → add content → see 


## Identified Risks
- Agentic development velocity outpacing verification - bugs compound silently
- No visible test suite in file manifest
- Multiple node dispatch without coordination may create merge conflicts


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
