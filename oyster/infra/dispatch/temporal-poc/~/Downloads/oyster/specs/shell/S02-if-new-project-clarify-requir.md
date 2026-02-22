---
task_id: S02-if-new-project-clarify-requir
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
if new project: clarify requirements before proceeding (what does 'shell' do?)


## Identified Risks
- Proceeding without clear project definition will create wasted effort
- Autonomous discovery on non-existent codebase will generate hallucinated priorities


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
