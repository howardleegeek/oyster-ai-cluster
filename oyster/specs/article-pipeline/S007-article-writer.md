---
task_id: S007-article-writer
project: article-pipeline
priority: 0
estimated_minutes: 40
depends_on: ["S006-article-outliner"]
modifies: ["oyster/social/article-pipeline/article_writer.py"]
executor: glm
---

## 目标
Generate full 2000+ word articles from outlines. Section-by-section generation for quality and coherence.

## 约束
- Python 3.11+
- Input: ArticleOutline from outliner
- Output: Article pydantic model with fields:
  - title, subtitle, author (default "Oyster Labs")
  - sections: List[ArticleSection] each with heading, body (markdown), word_count
  - total_words: int
  - seo_meta_description: str (150-160 chars)
  - tags: List[str]
  - created_at: datetime
  - status: draft | reviewed | published
- Generation strategy: **section-by-section** (not one giant prompt)
  - For each section in outline: generate 200-400 words using section context + previous sections summary
  - This ensures coherence and stays within LLM context limits
- LLM settings: temperature=0.7, max_tokens=2000 per section
- Include code examples where relevant (fenced markdown)
- Include data points and statistics (LLM should cite plausible sources)
- Tone: match outline.tone

## 验收标准
- [ ] ArticleWriter class with `async def write_article(outline: ArticleOutline) -> Article`
- [ ] Section-by-section generation with context passing
- [ ] Total word count >= 2000
- [ ] Proper markdown formatting
- [ ] pytest test passes with mock LLM

## 不要做
- Don't publish (separate spec)
- Don't generate images (separate spec)
- Don't modify outliner code
