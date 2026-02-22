---
task_id: S03-if-not-exists-clonecreate-pr
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
if not exists, clone/create project before dispatching tasks


## Identified Risks
- Dispatch may be pointing to non-existent directory causing silent failures
- Autonomous discovery on missing codebase will produce no useful output
- Time waste if tasks dispatched to phantom project


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
