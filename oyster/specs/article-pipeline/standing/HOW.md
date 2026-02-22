# HOW: Article Pipeline

Architecture: Trend Aggregator (Google Trends + Reddit + TwitFast adapters) → Trend Ranker (brand relevance scoring) → Article Outliner (LLM-generated structured outlines) → Article Writer (section-by-section generation, 2000+ words) → Quality Gate (readability, SEO, AI slop detection) → Reviser (targeted fixes) → X Article Publisher (CDP automation) → Tweet Thread Splitter + Publisher. Python 3.11+, async throughout, SQLite for state, GLM-4 for content generation.
