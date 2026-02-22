# HOW: Marketing Stack

Architecture: Common platform layer (queue, rate limiter, quality gate, LLM client) → Platform adapters (Twitter, Bluesky, LinkedIn, Discord, Email, Reddit) → n8n workflow orchestration → Analytics dashboards (PostHog + Plausible). All tools self-hosted on GCP/UpCloud. Python 3.11+ backend, FastAPI for APIs, SQLite for local state, PostgreSQL for shared data. ClawMarketing frontend integrates widgets for analytics, calendar, CRM, and SEO monitoring.
