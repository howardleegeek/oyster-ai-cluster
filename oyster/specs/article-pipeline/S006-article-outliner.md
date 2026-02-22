---
task_id: S006-article-outliner
project: article-pipeline
priority: 0
estimated_minutes: 30
depends_on: ["S005-trend-ranker"]
modifies: ["oyster/social/article-pipeline/article_outliner.py"]
executor: glm
---

## 目标
Generate article outlines from ranked trends. Each outline is a structured plan for a 2000+ word article.

## 约束
- Python 3.11+
- Input: RankedTrend from trend_ranker
- Output: ArticleOutline pydantic model with fields:
  - title: str (SEO-optimized, 60-80 chars)
  - hook: str (opening paragraph hook, 2-3 sentences)
  - sections: List[Section] each with heading, key_points (3-5 bullets), target_words (200-400)
  - conclusion_angle: str
  - target_audience: str
  - seo_keywords: List[str] (5-8 keywords)
  - estimated_words: int (target 2000-3000)
  - tone: str (authoritative, conversational, technical)
- Use LLM (GLM-4 via httpx) for outline generation
- LLM endpoint from env: LLM_API_URL, LLM_API_KEY
- Prompt template: "You are a senior tech editor at a leading AI publication..."
- Must have 5-7 sections minimum

## 验收标准
- [ ] ArticleOutliner class with `async def generate_outline(trend: RankedTrend) -> ArticleOutline`
- [ ] ArticleOutline pydantic model with validation
- [ ] LLM prompt produces structured JSON outline
- [ ] Fallback: retry up to 3 times if LLM returns malformed JSON
- [ ] pytest test passes with mock LLM response

## 不要做
- Don't write the full article (just outline)
- Don't call any external APIs besides LLM
