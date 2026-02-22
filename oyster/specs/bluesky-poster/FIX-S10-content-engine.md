---
task_id: FIX-S10-content-engine
project: bluesky-poster
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S10-content-engine  
project: bluesky-poster  
priority: 2  
depends_on: []  
modifies: ["bluesky/content_engine.py", "tests/test_content_engine.py"]  
---  
## Goal  
Fix the ContentEngine implementation to generate and schedule posts correctly without lease expiration errors.  

## Technical approach  
1. **Error Handling**: Implement retry logic with exponential backoff for LLM client calls and template generation to handle transient failures.  
2. **Lease Management**: Ensure that lease renewal is handled correctly by adding a check for lease expiration before task execution and renewing it if necessary.  
3. **Task Simplification**: Break down the `generate_post` function into smaller, manageable asynchronous tasks to prevent timeouts.  
4. **Logging**: Add detailed logging for lease management and task execution to aid in debugging.  
5. **Testing**: Create unit tests for the `ContentEngine` class to verify correct behavior and error handling.  

## Constraints  
- Use only standard Python libraries.  
- Ensure compatibility with the existing `BlueskyQueue` and `RateLimiter` classes.  
- Do not modify the external interfaces of `ContentEngine` unless absolutely necessary.  
- Maintain the content mix enforcement (25% emotional, 25% questions, etc.).  
- Avoid introducing new external dependencies.  

## Acceptance criteria  
- The `ContentEngine` successfully generates and schedules posts without encountering lease expiration errors.  
- The implementation includes retry logic for LLM client calls and template generation.  
- Lease renewal is handled correctly before task execution.  
- The `generate_post` function is broken down into smaller, asynchronous tasks.  
- Detailed logging is in place for lease management and task execution.  
- Unit tests in `tests/test_content_engine.py` cover:  
  - Successful post generation and scheduling.  
  - Handling of LLM client failures and template fallbacks.  
  - Lease renewal and expiration handling.  
  - Content mix enforcement.  
  - Deduplication of recent posts.  
- The tests pass consistently without errors.