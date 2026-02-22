---
task_id: S02-do-a-focused-tech-debt-pass-to
project: clawmarketing
priority: 2
estimated_minutes: 30
depends_on: []
---
## Goal
do a focused tech-debt pass to define canonical code paths (single frontend sour


## Identified Risks
- Duplicate/parallel code paths can cause silent regressions when fixes land in the wrong copy.
- Optimizing CMP alone can produce local maxima that do not improve revenue or qualified leads.
- Automated multi-channel dispatch can amplify low-quality experiments without strict guardrails and rollback.


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
