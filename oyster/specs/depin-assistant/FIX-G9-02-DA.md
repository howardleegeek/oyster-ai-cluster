---
task_id: FIX-G9-02-DA
project: depin-assistant
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-G9-02-DA  
project: depin-assistant  
priority: 2  
depends_on: []  
modifies: ["src/monitoring/metrics.js", "src/monitoring/middleware.js", "tests/monitoring/metrics.test.js"]  
---  
## Goal  
Implement and test Prometheus metrics for API response times and error rates.  

## Technical approach  
1. Utilize the Prometheus client library in Node.js to collect metrics.  
2. Develop middleware to track API response times and error rates, integrating it into the existing Express application.  
3. Implement unit tests using Jest to verify that metrics are correctly recorded and exposed.  
4. Ensure no more than 3 new files are created, adhering to the existing codebase structure.  

## Constraints  
- Modify only the specified files, creating no more than 3 new files.  
- Use standard Node.js tools and libraries (e.g., Express, Prometheus client).  
- Avoid using TODO/FIXME comments or placeholder code.  
- Ensure all tests pass without errors.  

## Acceptance criteria  
- [x] API response times are tracked and exposed as Prometheus metrics.  
  - Metrics include summary statistics (e.g., histogram) for response times.  
- [x] Error rates are tracked and exposed as Prometheus metrics.  
  - Metrics include a counter for total errors and a rate metric.  
- [x] All Prometheus metrics are accessible via the `/metrics` endpoint.  
- [x] Jest tests pass, verifying the correct collection and exposure of metrics.  
- [x] No new linting errors are introduced.