---
task_id: S009-article-reviser
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S008-article-quality-gate"]
modifies: ["oyster/social/article-pipeline/article_reviser.py"]
executor: glm
---

## 目标
Revise articles that scored "revise" from quality gate. Fix specific issues identified in QualityReport.

## 约束
- Python 3.11+
- Input: Article + QualityReport
- Output: revised Article
- Revision strategies:
  - word_count low → expand weakest sections via LLM
  - readability too high → simplify language via LLM
  - section_balance off → rewrite longest section to be more concise
  - spam_score high → replace flagged AI slop phrases
  - seo_score low → inject keywords naturally into intro and conclusion
- Max 2 revision rounds (if still fails after 2, mark as needs_human_review)
- LLM used only for expansion/rewriting, not for scoring

## 验收标准
- [ ] ArticleReviser class with `async def revise(article: Article, report: QualityReport) -> Article`
- [ ] Targeted revisions based on specific quality issues
- [ ] Max 2 rounds enforcement
- [ ] AI slop replacement list (at least 20 phrases)
- [ ] pytest test passes

## 不要做
- Don't re-evaluate (quality gate is separate)
- Don't rewrite from scratch
