---
task_id: FIX-FIX-G6-10-CV
project: clawvision
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-FIX-G6-10-CV  
project: clawvision  
priority: 2  
depends_on: []  
modifies: [  
  "src/services/dynamic_landing.py",  
  "src/api/routes/landing.py",  
  "tests/test_dynamic_landing.py"  
]  
---  
## Goal  
Implement dynamic landing page personalization with visitor segmentation and robust Git operations handling to prevent lease expiration issues.

## Technical approach  
- Refactor `DynamicLandingService` to dynamically render content based on visitor segmentation using Referrer, geolocation, and device type.  
- Implement the `VisitorSegmentor` class to categorize visitors accurately.  
- Update the API layer by adding the `/landing/{page_id}/render` endpoint, ensuring it returns personalized content variants.  
- Enhance Git operation handling by verifying repository URLs and implementing retry mechanisms for cloning processes to prevent lease expiration.  
- Write comprehensive unit tests for `DynamicLandingService`, `VisitorSegmentor`, and the new API endpoint to ensure functionality and prevent future lease issues.

## Constraints  
- Modify only the specified files without creating new files.  
- Use standard Python tools (e.g., `requests`, `git` Python library) without relying on obscure CLIs.  
- Do not leave any TODO/FIXME/placeholder comments in the code.  
- Ensure the implementation does not refactor unrelated existing code or alter UI/CSS.  
- Keep rendering response time under 200ms for all test cases.

## Acceptance criteria  
- [x] The system correctly segments visitors based on Referrer, geolocation, and device type, verified by unit tests.  
- [x] The `/landing/{page_id}/render` endpoint returns different page variants for different visitor segments, tested with multiple scenarios.  
- [x] The rendering response time is consistently under 200ms for all test cases, measured using a benchmarking tool.  
- [x] All tests in `tests/test_dynamic_landing.py` pass successfully (pytest should be all green).  
- [x] Git operations are handled without lease expiration errors, verified by unit tests that simulate cloning processes and handle retries gracefully.  
- [x] The implementation is robust and does not alter unrelated code or UI/CSS, verified by code review and linting tools.