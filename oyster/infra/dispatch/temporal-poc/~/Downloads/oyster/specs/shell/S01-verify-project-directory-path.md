---
task_id: S01-verify-project-directory-path
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
verify project directory path - create ~/downloads/shell if this is correct loca


## Identified Risks
- Path mismatch - project may exist elsewhere under different name
- Template mismatch suggests dispatch system has no prior context for this project type
- Starting without clear spec leads to wasted cycles


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
