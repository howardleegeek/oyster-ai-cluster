---
task_id: S03-define-autonomous-discovery
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
define 'autonomous discovery' concretely: what files to scan, what patterns to f


## Identified Risks
- Temporal migration may have lost edge case handling that the old 12K lines covered
- Metrics collection might be silently failing (wrong DB connection, missing table)
- Worker could be running but not receiving tasks (queue mismatch, wrong namespace)


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
