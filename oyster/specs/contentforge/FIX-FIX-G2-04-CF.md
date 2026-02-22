---
task_id: FIX-FIX-G2-04-CF
project: contentforge
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-FIX-G2-04-CF  
project: contentforge  
priority: 2  
depends_on: []  
modifies: ["app/routes.py", "tests/test_routes.py"]  
---  
## Goal  
Implement JWT-based user authentication for the content generation API endpoint.  

## Technical approach  
1. In `app/routes.py`, add a `@jwt_required` decorator to the content generation endpoint using the `Flask-JWT-Extended` library for authentication.  
2. Configure the JWT secret key and initialize the JWT manager in the Flask app.  
3. Update the content generation route to require a valid JWT token for access.  
4. In `tests/test_routes.py`, write unit tests using `pytest` and `pytest-flask` to verify:  
   - Accessing the endpoint without a token returns a 401 Unauthorized response.  
   - Accessing the endpoint with an invalid token returns a 401 Unauthorized response.  
   - Accessing the endpoint with a valid token succeeds and returns the expected content.  

## Constraints  
- Modify only `app/routes.py` and `tests/test_routes.py`.  
- Use the `Flask-JWT-Extended` library for JWT handling.  
- Ensure all tests pass without any TODOs or placeholders.  
- Do not introduce new files or modify existing files other than those specified.  

## Acceptance criteria  
- [x] The content generation API endpoint requires a valid JWT token for access.  
- [x] A request without a token to the endpoint returns a 401 Unauthorized response.  
- [x] A request with an invalid token to the endpoint returns a 401 Unauthorized response.  
- [x] A request with a valid token to the endpoint returns the expected content.  
- [x] All unit tests in `tests/test_routes.py` pass using `pytest`.