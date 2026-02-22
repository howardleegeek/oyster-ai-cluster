---
task_id: FIX-G2-04-CF
project: contentforge
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G2-04-CF  
project: contentforge  
priority: 2  
depends_on: []  
modifies: ["app/routes.py", "tests/test_routes.py"]  
---  
## Goal  
Implement JWT-based user authentication and authorization for the content generation API endpoint.  

## Technical approach  
1. In `app/routes.py`, add a decorator to protect the content generation endpoint using JWT for user authentication.  
2. Verify the JWT token's validity and extract user information to enforce authorization checks.  
3. Update the existing content generation route to require a valid JWT token for access.  
4. In `tests/test_routes.py`, write unit tests to verify that:  
   - Accessing the endpoint without a token returns a 401 Unauthorized response.  
   - Accessing the endpoint with an invalid token returns a 401 Unauthorized response.  
   - Accessing the endpoint with a valid token succeeds and returns the expected content.  

## Constraints  
- Modify only `app/routes.py` and `tests/test_routes.py`.  
- Do not introduce new files or modify existing files other than those specified.  
- Use standard Python libraries (e.g., PyJWT, Flask) for JWT handling.  
- Ensure all tests pass without any TODOs or placeholders.  

## Acceptance criteria  
- [x] The content generation API endpoint requires a valid JWT token for access.  
- [x] A request without a token to the endpoint returns a 401 Unauthorized response.  
- [x] A request with an invalid token to the endpoint returns a 401 Unauthorized response.  
- [x] A request with a valid token to the endpoint returns the expected content.  
- [x] All unit tests in `tests/test_routes.py` pass with pytest.