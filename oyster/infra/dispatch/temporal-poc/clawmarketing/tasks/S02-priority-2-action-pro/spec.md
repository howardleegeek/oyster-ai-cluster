## Goal
{'priority': 2, 'action': 'production deployment dry-run', 'rationale': 'docker-


## Identified Risks
- Spec debt: 48 specs without clear done/pending status could hide unfinished work
- Integration surface: Bluesky + Threads + existing platforms = exponential test matrix
- Technical debt: Empty docker-compose.prod.yml blocks production path


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

## FALLBACK PROTOCOL INITIATED
Previous attempts continuously failed. Final error:
```
Activity task failed
```

**CRITICAL INSTRUCTION**: Abandon your previous approach. Simplify your solution, use alternative methods, or stub the functionality safely. Do NOT repeat the same mistakes.