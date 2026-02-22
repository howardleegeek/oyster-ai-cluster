---
task_id: FIX-S049-n8n-posthog-web
project: marketing-stack
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S049-n8n-posthog-web
project: marketing-stack
priority: 2
depends_on: []
modifies: ["n8n-workflows/posthog-webhook-workflow.json", "tests/posthog-webhook-test.js"]
---
## Goal
Create a functional n8n workflow that processes PostHog webhook events and routes them to the appropriate destinations based on event type.

## Technical approach
1. Utilize the n8n Webhook node to receive PostHog events.
2. Parse the event payload using the Function node with standard JavaScript/Node.js.
3. Implement Switch nodes to route events based on the event type (conversion, error, milestone).
4. Use the HTTP Request node to send conversion events to Twenty CRM.
5. Use the Slack node to send error events as Slack alerts.
6. Use the HTTP Request node to log all events to Directus.
7. Write unit tests using a standard testing framework (e.g., Jest) to verify the workflow's functionality.

## Constraints
- Use only standard Python/Node.js tools and n8n built-in nodes.
- Do not implement a custom analytics engine.
- Do not store events beyond the logging step.
- Do not implement a real-time dashboard.
- Ensure the workflow is modular and maintainable.

## Acceptance criteria
- [x] The n8n workflow JSON file is created and stored in `n8n-workflows/posthog-webhook-workflow.json`.
- [x] The workflow receives PostHog events via a webhook.
- [x] The event payload is parsed correctly, and event properties are accessible.
- [x] Conversion events are routed to Twenty CRM.
- [x] Error events are sent as Slack alerts.
- [x] All events are logged to Directus.
- [x] The workflow is successfully imported and runs without errors in the n8n instance.
- [x] Unit tests in `tests/posthog-webhook-test.js` cover the following scenarios:
  - Successful processing of a conversion event.
  - Successful processing of an error event.
  - Successful processing of a milestone event.
  - Proper logging of all events to Directus.
  - Handling of malformed event payloads.