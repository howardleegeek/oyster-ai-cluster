# Flight Rules (AI OS) — Howard Infra Edition
> These rules are non-negotiable. If any instruction conflicts, follow this file.


## FR-000 Priority
- This file overrides all other guidance in ai_os.


## Workspace & Safety
### FR-001 Workspace Boundary (WRITE)
- All write operations MUST stay inside:
  `/Users/howardli/Downloads/infrastructure/ai_os/`
- Writing outside is forbidden even if user asks.
- Read outside is allowed only for analysis.


### FR-002 No Skeleton Rebuild
- ai_os skeleton already exists.
- NEVER regenerate directory trees or duplicate foundation templates.
- Only incremental updates: add new artifacts, append logs, or patch specific files.


### FR-003 No Fake Execution
- Do not claim commands ran unless you actually ran them.
- When unsure, output the exact command to run.


## Logging & Truth Sources
### FR-010 Append-only Logs
- DIALOGUE*.md and DIALOGUE_LOG.md are append-only.
- Never edit or delete historical entries—only append new sections.


### FR-011 Tasks Single Source of Truth
- Tasks must live ONLY in:
  - `ai_os/TASKS_GLOBAL.md`, or
  - `ai_os/projects/<P>/TASKS.md`
- Any "task-like" user message must become a task entry.


### FR-012 Data Retention
- Do NOT delete data unless user explicitly says "delete".
- Otherwise move/archive/merge.


## Routing & Artifacts
### FR-020 Artifact Routing Required
Before creating any artifact:
1) Identify artifact type (Content/BD/Ops/Research/Infra)
2) Choose destination path per ROUTING_RULES.md
3) Create folder `YYYY-MM-DD_slug/`
4) Write main content to `index.md`
5) Update TASKS + append DIALOGUE
6) Emit an event (FR-030)


### FR-021 Inbox Is Temporary
- If destination is unclear, write to `projects/<P>/inbox/` and create a routing task.


### FR-022 Outputs Must Be Bucketed
- Artifacts must be stored under `outputs/{content,bd,ops,misc}/...`
- Never dump directly into `outputs/` root.


## Time & Scheduling
### FR-025 Time-intent Capture
If user mentions time intent (e.g., tomorrow, next week, date):
- Add/Update a task with `due: YYYY-MM-DD` (best-effort parse).
- If ambiguous, still create the task with `due: TBD` and ask one follow-up.


## Event Sourcing (System Truth)
### FR-030 Every Change Emits an Event
- Every artifact created/moved/updated must write an event line to NDJSON:
  - Global: `ai_os/events/YYYY-MM.ndjson`
  - Project (optional): `ai_os/projects/<P>/events/YYYY-MM.ndjson`
- Event must be appended as a single JSON line (no pretty print).


### FR-031 Events Are Immutable
- Events are append-only. Never rewrite old events.


## Cross-project & Risk Gate
### FR-040 One Project Per Session
- Default to one project per session.
- Cross-project requests must be split into blocks and logged separately.


### FR-041 Root Repo File Changes Require Approval
- Files outside ai_os (repo root: capabilities.py, docker-compose.yml, .env*, .sops.yaml) are **high-risk**.
- You MUST produce "impact analysis + plan" and wait for explicit user approval before modifying.


## Quality Gate
### FR-050 Done Means Recorded
A task is not "done" unless:
- The artifact exists in the correct routed path, AND
- TASKS updated, AND
- DIALOGUE appended, AND
- Event appended.
