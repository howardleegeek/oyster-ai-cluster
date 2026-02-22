---
task_id: J10-test-runbook
project: marketing-stack
priority: 5
estimated_minutes: 30
depends_on: []
modifies: ["oyster/docs/runbook/marketing-stack-ops.md"]
executor: glm
---
## 目标
Write ops runbook: restart procedures, backup/restore, monitoring endpoints, alert escalation, troubleshooting

## 约束
- Section 1: Service restart commands (n8n, Listmonk, Postiz, etc.)
- Section 2: Backup/restore procedures for databases
- Section 3: Health check endpoints for all services
- Section 4: Alert escalation matrix
- Section 5: Common issues + solutions
- Markdown format, clear step-by-step

## 验收标准
- [ ] marketing-stack-ops.md created in docs/runbook/
- [ ] Restart procedures for all services documented
- [ ] Backup/restore steps tested and validated
- [ ] Health check endpoints listed with curl examples
- [ ] Alert escalation matrix clear
- [ ] 10+ common troubleshooting scenarios included
- [ ] Runbook reviewed for clarity

## 不要做
- No theoretical content (only tested procedures)
- No vendor-specific jargon without explanation
- No incomplete sections
