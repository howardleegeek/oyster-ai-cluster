---
task_id: S02-run-a-focused-audit-of-the-2-f
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
run a focused audit of the 2 failed default-template trajectories and convert fi


## Identified Risks
- Current green status may be a false positive if tests are too shallow; cleanup-related breakage in Web3 integrations may go undetected until later.
- Advisor instability (timeouts/auto-approve) can steer autonomous discovery toward low-quality or repetitive tasks despite good CMP.


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
