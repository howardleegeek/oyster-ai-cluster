# Deep Think Factory — Temporal + Multi-Advisor 24h Autonomous Dev

**Date:** 2026-02-21
**Status:** Approved, implementing
**Scope:** ClawMarketing + Shell (pilot)

## Problem

Current factory_daemon.py runs 24h but:
- SQLite locks cause spec registration failures
- 162 slots, <1% utilization (1 running task)
- No quality gate — blind code stacking
- No learning from past failures

## Solution: Stitched Architecture

Combine proven OSS components into a Temporal-native deep-thinking factory.

### Component Sources

| Component | Source | What We Take |
|-----------|--------|-------------|
| Self-optimization | OpenAI GEPA (`pip install gepa`) | Evolutionary prompt improvement |
| Agent evolution | EvoAgentX (`pip install evoagentx`) | Memory modules, workflow optimization |
| 24h loop | Ralph (frankbria/ralph-claude-code) | Circuit breaker, dual-condition exit |
| Stuck detection | OpenHands (All-Hands-AI/OpenHands) | 5 stuck-loop patterns |
| Multi-agent | AutoGen (`pip install autogen-agentchat`) | MagenticOne dual ledger pattern |
| Template selection | HGM (metauto-ai/HGM) | Thompson Sampling + CMP scoring |
| Batch execution | SWE-agent | YAML config, trajectory logging |
| Self-correction | Aider | Bounded reflection (max 3), dual-model |

### 4-Phase Cycle

```
Think (参谋团共识) → Build (精准执行) → Review (交叉审查) → Learn (进化记忆)
     ↑                                                          │
     └──────────────────────────────────────────────────────────┘
```

### File Structure

```
temporal-poc/factory/
├── __init__.py
├── orchestrator.py     # 24h loop (Temporal Schedule)
├── think.py            # Multi-advisor consensus
├── build.py            # Bounded execution
├── review.py           # Cross-review + self-debug
├── learn.py            # GEPA evolution + Thompson sampling
├── advisors.py         # Opus/Codex/Antigravity wrappers
├── stuck_detector.py   # Ported from OpenHands
├── circuit_breaker.py  # Ported from Ralph
├── memory.py           # Trajectory + versioned prompts
└── config.py           # YAML declarative config
```

### What We Keep

- task-wrapper.sh (battle-tested executor)
- Temporal POC (workflows.py, activities.py, worker.py)
- 12 worker nodes, 162 slots

### What We Replace

- factory_daemon.py → new orchestrator
- dispatch.py + SQLite → Temporal state
- guardian.py → Temporal heartbeat
- dispatch-controller.py → new orchestrator
