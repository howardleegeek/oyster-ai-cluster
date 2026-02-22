---
task_id: FIX-G14-01-CV
project: clawvision
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G14-01-CV  
project: clawvision  
priority: 2  
depends_on: []  
modifies: ["api/routes/image_upload.py", "tests/test_image_upload.py"]  

---
## Goal
Implement a robust image upload API endpoint that supports batch uploads, validates files, and stores images with proper error handling.

## Technical approach
1. Add a POST endpoint `/upload-images` in `api/routes/image_upload.py` using FastAPI's `UploadFile` to handle batch uploads.
2. Implement file type and size validation for each uploaded file.
3. Store images in a temporary directory and return a detailed processing status for each image.
4. Update `tests/test_image_upload.py` with pytest test cases to cover:
   - Successful single and multiple image uploads.
   - Uploads with invalid file types.
   - Uploads exceeding size limits.
   - Edge cases such as empty uploads.

## Constraints
- Modify only the specified files; do not create new files.
- Use standard Python libraries (e.g., FastAPI, pytest, tempfile).
- Ensure no leftover TODOs, FIXMEs, or placeholders in the code.
- Keep the implementation simple and avoid over-engineering.

## Acceptance criteria
- [x] The `/upload-images` endpoint successfully handles single image uploads and returns a processing status.
- [x] The endpoint successfully handles multiple image uploads and returns a processing status for each image.
- [x] Uploads with non-image file types return a clear error message indicating invalid file type.
- [x] Uploads exceeding the size limit return a clear error message indicating the size constraint.
- [x] All test cases in `tests/test_image_upload.py` pass without errors.
- [x] The implementation does not introduce any new linting issues.