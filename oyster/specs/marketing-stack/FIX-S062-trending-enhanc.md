---
task_id: FIX-S062-trending-enhanc
project: marketing-stack
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S062-trending-enhanc  
project: marketing-stack  
priority: 2  
depends_on: []  
modifies: ["oyster/social/bluesky-poster/bluesky/trending.py"]  
---
## Goal
Implement cross-platform trend aggregation, relevance scoring, and topic suggestion in `trending.py` with caching and comprehensive tests.

## Technical approach
1. **Trend Aggregation**: Utilize existing APIs for Twitter, Bluesky, and Reddit to fetch trending data. Aggregate the trends by merging the fetched data.
2. **Relevance Scoring**: Implement a scoring algorithm that considers volume, velocity, and relevance to brand personas. Use predefined weights for each factor.
3. **Topic Suggestion**: Develop a method to suggest 3-5 content topics based on the aggregated trends using keyword extraction and trend analysis.
4. **Caching**: Implement caching for the fetched trends using Python's `cachetools` library to store data for 1 hour, reducing unnecessary API calls.
5. **Testing**: Write comprehensive `pytest` tests to ensure each method (`get_relevant_trends` and `suggest_content_topics`) works as expected and that the caching mechanism is effective.

## Constraints
- Only use standard Python libraries and tools (e.g., `requests`, `cachetools`, `pytest`).
- Do not implement auto-posting, sentiment analysis, or UI visualization.
- Ensure that the caching mechanism reduces API calls by at least 50%.
- The trend aggregation must include data from Twitter, Bluesky, and Reddit.
- The `get_relevant_trends` method must return a ranked list of trends based on the scoring algorithm.
- The `suggest_content_topics` method must return 3-5 valid topic ideas per trend.

## Acceptance criteria
- [x] `trending.py` is updated with cross-platform trend aggregation logic.
- [x] The trend scoring algorithm is implemented and correctly ranks trends based on volume, velocity, and relevance.
- [x] The `get_relevant_trends(brand_persona)` method returns a ranked list of trends for each brand persona.
- [x] The `suggest_content_topics(trend)` method returns 3-5 valid topic ideas per trend.
- [x] Caching is implemented using `cachetools` and reduces API calls by at least 50%.
- [x] All `pytest` tests pass, including tests for trend aggregation, scoring, topic suggestion, and caching.
- [x] The CLI command `python -m bluesky.trending --persona <name>` works and returns relevant trends for the specified persona.