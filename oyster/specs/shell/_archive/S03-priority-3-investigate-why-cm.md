---
task_id: S03-priority-3-investigate-why-cm
project: shell
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
priority 3: investigate why cmp is only 0.75 - what's causing that 25% failure? 


## Identified Risks
- Optimistic bias: 1 success = 0 failures is meaningless sample size. Real failures start at task #5-10
- Template tunnel vision: 'default is best' might just mean 'others are worse' - all templates could be mediocre
- Discovery drift: 'autonomous discovery' without constraints could burn weeks on exploratory work with no deliverable


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
