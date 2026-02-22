---
task_id: S008-article-quality-gate
project: article-pipeline
priority: 0
estimated_minutes: 25
depends_on: ["S007-article-writer"]
modifies: ["oyster/social/article-pipeline/article_quality_gate.py"]
executor: glm
---

## 目标
Quality gate for generated articles. Scores and filters articles before distribution.

## 约束
- Python 3.11+
- Input: Article from writer
- Output: QualityReport with fields:
  - overall_score: float (0.0-1.0)
  - word_count_ok: bool (>= 1800)
  - readability_score: float (Flesch-Kincaid, target 40-60 for tech content)
  - section_balance: float (no section > 40% of total words)
  - has_code_examples: bool
  - has_data_points: bool
  - seo_score: float (keyword density 1-3%, title contains keyword)
  - spam_score: float (low = good, detect AI slop: "delve", "tapestry", "landscape of")
  - verdict: pass | revise | reject
- Pass threshold: overall_score >= 0.7
- Revise: 0.5-0.7 (send back to writer with feedback)
- Reject: < 0.5

## 验收标准
- [ ] ArticleQualityGate class with `def evaluate(article: Article) -> QualityReport`
- [ ] All scoring dimensions implemented
- [ ] AI slop detection (list of flagged phrases)
- [ ] Readability calculation (simplified Flesch-Kincaid)
- [ ] pytest test passes

## 不要做
- No LLM calls (pure algorithmic evaluation)
- No external APIs
