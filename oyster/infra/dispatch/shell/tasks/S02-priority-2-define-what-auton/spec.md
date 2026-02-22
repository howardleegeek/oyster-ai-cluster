## Goal
priority 2: define what 'autonomous discovery' actually delivers - a spec? a pat


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