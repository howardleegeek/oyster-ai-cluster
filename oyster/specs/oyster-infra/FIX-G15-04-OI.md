---
task_id: FIX-G15-04-OI
project: oyster-infra
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G15-04-OI  
project: oyster-infra  
priority: 2  
depends_on: []  
modifies: ["src/security.py", "tests/test_security.py"]  
---  
## Goal  
Implement and test a `sanitize_input` function to prevent SQL injection by sanitizing user inputs using Python's standard libraries.  

## Technical approach  
1. Add a `sanitize_input` function in `src/security.py` that sanitizes user inputs by escaping special SQL characters using Python's `re` and `html` modules.  
2. Update `tests/test_security.py` to include unit tests for the `sanitize_input` function, ensuring it correctly escapes SQL-specific characters and handles various input cases.  
3. Ensure no external dependencies or obscure tools are introduced.  

## Constraints  
- Modify only `src/security.py` and `tests/test_security.py`.  
- Do not introduce any `TODO`, `FIXME`, or placeholder comments.  
- Use only standard Python libraries (`re`, `html`).  
- Include at least 5 test cases covering typical and edge cases.  
- Ensure existing unit tests remain unaffected and pass.  

## Acceptance criteria  
- [x] The `sanitize_input` function correctly escapes SQL-specific characters in sample inputs.  
  - Example: `sanitize_input("user' OR '1'='1")` returns `"user'' OR ''1''=''1"`.  
- [x] All existing unit tests in `tests/test_security.py` pass after the change.  
- [x] New unit tests are added to cover the `sanitize_input` functionality, including:  
  - Testing with typical SQL injection attempts.  
  - Testing with empty strings and non-string inputs.  
  - Testing with strings containing only safe characters.  
  - Testing with Unicode characters.  
- [x] `pytest` passes with zero test failures or errors.