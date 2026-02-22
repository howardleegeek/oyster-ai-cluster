---
task_id: FIX-G14-04-CV
project: clawvision
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G14-04-CV  
project: clawvision  
priority: 2  
depends_on: []  
modifies: ["api/routes/image_analysis.py", "tests/test_image_analysis.py"]  

---
## Goal
Implement a `/analyze-image` POST endpoint in the API that performs object detection and sentiment analysis on uploaded images.

## Technical approach
1. Add a POST endpoint `/analyze-image` in `api/routes/image_analysis.py` to handle image uploads.
2. Utilize a pre-trained AI model (e.g., YOLO for object detection and VADER for sentiment analysis) to process the image.
3. Return a JSON response containing detected objects and sentiment analysis results.
4. Implement error handling to return appropriate error messages for invalid inputs or processing failures.
5. Write unit tests in `tests/test_image_analysis.py` to validate the functionality, including successful analysis and error scenarios.

## Constraints
- Modify only the specified files.
- Use standard Python libraries and tools (e.g., FastAPI, PIL, transformers).
- Do not add TODO/FIXME comments or placeholders.
- Ensure all tests pass without errors.

## Acceptance criteria
- [x] The `/analyze-image` endpoint accepts image files via POST requests.
- [x] The endpoint returns a JSON response with detected objects and sentiment analysis.
- [x] The response includes error messages for invalid inputs or processing failures.
- [x] All tests in `tests/test_image_analysis.py` pass successfully.
- [x] The implementation does not introduce new linting errors.