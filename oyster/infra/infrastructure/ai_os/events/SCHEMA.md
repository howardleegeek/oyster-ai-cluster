# AI OS Event Schema (NDJSON)
All events are stored as NDJSON (one JSON object per line).
Primary store: `ai_os/events/YYYY-MM.ndjson` (append-only)


## Required Fields
- ts: ISO8601 timestamp with timezone offset (e.g., 2026-02-14T22:31:05-08:00)
- actor: "user" | "agent"
- project: "GLOBAL" | "Puffy" | "Oyster" | "Growth" | "Research" | "Infra"
- type: event type (see list)
- summary: short human-readable sentence
- refs: object with optional pointers (paths, task ids, urls)


## Recommended Fields
- session_id: optional unique id for the chat/session
- artifact_type: "content" | "bd" | "ops" | "research" | "infra" | "misc"
- artifact_path: relative path under ai_os/ if applicable
- task_ref: string reference like "projects/Oyster/TASKS.md#P0-3" (best-effort)
- meta: object for additional structured data (metrics, tags, due date, etc.)


## Event Types (Common)
- session.start
- session.end
- task.created
- task.updated
- task.completed
- artifact.created
- artifact.moved
- artifact.updated
- memory.episodic.created
- memory.semantic.updated
- rule.created
- rule.updated
- audit.storage
- brief.morning


## NDJSON Examples


{"ts":"2026-02-14T22:31:05-08:00","actor":"agent","project":"GLOBAL","type":"session.start","summary":"Started session focusing on Infra AI OS governance.","refs":{"path":"ai_os/"}}


{"ts":"2026-02-14T22:33:10-08:00","actor":"agent","project":"Infra","type":"rule.created","summary":"Added Flight Rules as non-negotiable operating constraints.","refs":{"artifact_path":"ai_os/flight_rules.md"},"artifact_type":"infra"}


{"ts":"2026-02-14T22:36:42-08:00","actor":"agent","project":"Infra","type":"artifact.created","summary":"Created event schema documentation for NDJSON event sourcing.","refs":{"artifact_path":"ai_os/events/SCHEMA.md"},"artifact_type":"infra"}


{"ts":"2026-02-14T22:41:02-08:00","actor":"agent","project":"Oyster","type":"task.created","summary":"Create BD outreach email to Sanctum and a follow-up playbook.","refs":{"task_file":"ai_os/projects/Oyster/TASKS.md"},"meta":{"priority":"P1","due":"2026-02-16","artifact_type":"bd"}}


{"ts":"2026-02-14T22:45:19-08:00","actor":"agent","project":"Oyster","type":"artifact.created","summary":"Drafted Sanctum outreach email + follow-up playbook.","refs":{"artifact_path":"ai_os/projects/Oyster/outputs/bd/2026-02-14_sanctum_outreach/index.md"},"artifact_type":"bd"}


{"ts":"2026-02-14T22:46:00-08:00","actor":"agent","project":"GLOBAL","type":"brief.morning","summary":"Generated morning brief from open tasks.","refs":{"artifact_path":"ai_os/logs/daily/2026-02-14_morning.md"}}


{"ts":"2026-02-14T22:47:12-08:00","actor":"agent","project":"GLOBAL","type":"audit.storage","summary":"Ran storage audit; no stale inbox artifacts found.","refs":{"artifact_path":"ai_os/logs/weekly/2026-02-14_storage_audit.md"}}
