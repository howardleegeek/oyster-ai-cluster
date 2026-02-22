---
task_id: F12-cm-auth-layer
project: marketing-stack
priority: 2
estimated_minutes: 25
depends_on: []
modifies: ["clawmarketing/backend/core/external_auth.py"]
executor: glm
---
## 目标
Add unified API auth layer for all external tool connections - store API keys in ~/.oyster-keys/, rotate every 90 days, health check endpoint per tool

## 约束
- Create core/external_auth.py module
- Load API keys from ~/.oyster-keys/<tool>.key
- Provide get_client(tool_name) function
- Add GET /health/external endpoint
- Check each tool API connectivity
- Return status per tool (healthy/degraded/down)

## 验收标准
- [ ] external_auth.py module created
- [ ] Loads keys from ~/.oyster-keys/
- [ ] get_client(tool_name) returns authenticated client
- [ ] GET /health/external endpoint implemented
- [ ] Tests connectivity to all external tools
- [ ] Returns JSON status per tool
- [ ] pytest tests/backend/core/test_external_auth.py passes

## 不要做
- Don't build key rotation automation yet
- Don't add OAuth flow UI
- Don't implement rate limit tracking
