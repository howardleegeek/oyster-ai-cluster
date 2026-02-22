---
task_id: FIX-S049-n8n-posthog-webhook
project: marketing-stack
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S049-n8n-posthog-webhook  
project: marketing-stack  
priority: 2  
depends_on: []  
modifies: ["n8n-workflows/posthog-events.json", "tests/posthog-webhook.test.js"]  
---
## Goal  
Create a functional n8n workflow that processes PostHog webhook events, routes them based on event type, and logs the events to Directus.

## Technical approach  
1. Use the n8n Webhook node to receive PostHog events.  
2. Parse the event payload using the Function node to extract event type and properties.  
3. Implement Switch nodes to route events based on their type (conversion/error/milestone).  
4. Use appropriate nodes to send conversions to Twenty CRM, errors to Slack, and all events to Directus for logging.  
5. Write unit tests using a standard testing framework (e.g., Jest) to verify webhook reception, correct routing, and logging functionality.

## Constraints  
- Use only standard n8n nodes and standard JavaScript/Python functions.  
- Do not implement any custom analytics or real-time dashboards.  
- Do not store events beyond the logging step in Directus.  
- Ensure the workflow is modular and readable.  
- Include error handling for failed API calls or parsing issues.

## Acceptance criteria  
- [x] Workflow JSON is correctly formatted and saved in `n8n-workflows/posthog-events.json`.  
- [x] The n8n instance successfully imports and runs the workflow without errors.  
- [x] The Webhook node receives and processes PostHog events as verified by test cases.  
- [x] Event type and properties are correctly parsed and routed:  
  - Conversions are sent to Twenty CRM.  
  - Errors are sent to Slack as alerts.  
  - All events are logged to Directus.  
- [x] Unit tests in `tests/posthog-webhook.test.js` cover:  
  - Successful reception of webhook events.  
  - Correct parsing and routing of different event types.  
  - Proper logging of events to Directus.  
  - Handling of error scenarios gracefully.  
- [x] The workflow avoids unnecessary data storage and does not implement unauthorized features.