---
task_id: FIX-G10-01-CV
project: clawvision
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G10-01-CV  
project: clawvision  
priority: 2  
depends_on: []  
modifies: ["src/api/security.py", "tests/test_security.py"]  

---  
## Goal  
Implement a functional JWT-based authentication mechanism in FastAPI with complete unit test coverage.

## Technical approach  
1. Utilize the `PyJWT` library to encode and decode JWT tokens.  
2. Implement a dependency function in `security.py` to validate JWT tokens for API routes.  
3. Create a middleware in `security.py` to automatically verify JWT tokens for protected routes.  
4. Write helper functions in `security.py` for generating and verifying JWT tokens.  
5. Develop unit tests in `tests/test_security.py` to ensure JWT generation, validation, and middleware functionality work as expected.

## Constraints  
- Only modify the specified files; do not create new files or alter existing file structures beyond necessity.  
- Avoid using obscure or non-standard Python libraries; stick to `PyJWT` and standard FastAPI utilities.  
- Ensure no `TODO`, `FIXME`, or placeholder comments remain in the code.  
- Write comprehensive unit tests covering JWT creation, validation, and middleware behavior.

## Acceptance criteria  
- [x] API routes decorated with the JWT dependency reject requests without a valid token.  
- [x] JWT tokens expire after the defined timeframe and cannot be used beyond expiration.  
- [x] The middleware correctly verifies JWT tokens and grants access to protected routes when valid.  
- [x] All unit tests in `tests/test_security.py` pass without errors.  
- [x] No linting issues are introduced in the modified files.