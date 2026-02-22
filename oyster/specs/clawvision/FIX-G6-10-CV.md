---
task_id: FIX-G6-10-CV
project: clawvision
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G6-10-CV  
project: clawvision  
priority: 2  
depends_on: []  
modifies: ["src/services/dynamic_landing.py", "src/api/routes/landing.py", "tests/test_dynamic_landing.py"]  
---  
## Goal  
Implement dynamic landing page personalization with visitor segmentation and handle Git operations correctly to prevent lease expiration issues.  

## Technical approach  
- Refactor the `DynamicLandingService` to handle dynamic content rendering based on visitor segmentation.  
- Implement the `VisitorSegmentor` to categorize visitors using Referrer, geolocation, and device type.  
- Update the API layer to include the `/landing/{page_id}/render` endpoint for rendering personalized content.  
- Ensure Git operations are correctly managed to prevent lease expiration by verifying repository URL and handling cloning processes robustly.  

## Constraints  
- Modify only the specified files without creating more than three new files.  
- Avoid using obscure CLIs; rely on standard Python/Node.js tools.  
- Do not leave any TODO/FIXME/placeholder comments in the code.  
- Include comprehensive tests to ensure functionality and prevent future lease issues.  
- Ensure the implementation does not refactor unrelated existing code or alter UI/CSS.  

## Acceptance criteria  
- [x] The system correctly segments visitors based on Referrer, geolocation, and device type.  
- [x] The `/landing/{page_id}/render` endpoint returns different page variants for different visitor segments.  
- [x] The rendering response time is under 200ms for all test cases.  
- [x] All tests in `tests/test_dynamic_landing.py` pass successfully (pytest should be all green).  
- [x] Git operations are handled without lease expiration errors, verified by ensuring the repository URL is correct and cloning processes are robust.