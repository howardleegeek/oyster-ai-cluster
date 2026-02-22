---
task_id: FIX-S027-twitter-adapter
project: marketing-stack
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S027-twitter-adapter
project: marketing-stack
priority: 2
depends_on: []
modifies: ["oyster/social/twitter/adapter.py", "tests/social/twitter/test_adapter.py"]
---
## Goal
Implement the PlatformAdapter Protocol in `oyster/social/twitter/adapter.py` with `post()`, `reply()`, `get_metrics()`, and `search()` methods, ensuring graceful handling of rate limiting and structured response returns.

## Technical approach
1. Refactor the core posting logic from `twitter-poster/twitter_poster.py` into a reusable module.
2. Integrate the refactored logic into `adapter.py` to implement the `post()` and `reply()` methods.
3. Utilize existing RapidAPI/CDP modes for communication with the Twitter API.
4. Implement `get_metrics()` to fetch engagement data from Twitter's API.
5. Implement `search()` to retrieve relevant tweets based on query parameters.
6. Ensure all methods handle rate limiting gracefully by implementing retry logic with exponential backoff.
7. Update `tests/social/twitter/test_adapter.py` to include unit tests for each method, ensuring adherence to the PlatformAdapter Protocol.

## Constraints
- Do not modify the existing RapidAPI/CDP integration code.
- Do not introduce new dependencies beyond the PlatformAdapter Protocol interface.
- Do not alter the `twitter-poster/twitter_poster.py` file directly; refactor logic into a separate module if necessary.
- Ensure all methods return structured responses that match the PlatformAdapter Protocol specifications.

## Acceptance criteria
- [x] `adapter.py` contains implementations for `post()`, `reply()`, `get_metrics()`, and `search()` methods adhering to the PlatformAdapter Protocol.
- [x] The `post()` method successfully posts tweets to Twitter using the existing RapidAPI/CDP integration.
- [x] The `reply()` method successfully replies to tweets using the existing RapidAPI/CDP integration.
- [x] The `get_metrics()` method returns accurate engagement data from Twitter.
- [x] The `search()` method returns relevant tweets based on provided query parameters.
- [x] All methods handle rate limiting gracefully, implementing retry logic with exponential backoff.
- [x] `tests/social/twitter/test_adapter.py` includes unit tests for each method, verifying correct behavior and adherence to the protocol.
- [x] All tests pass without errors.