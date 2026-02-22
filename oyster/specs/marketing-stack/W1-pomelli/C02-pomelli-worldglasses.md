---
task_id: C02-pomelli-worldglasses
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["docs/pomelli/brand-dna-worldglasses.json"]
executor: glm
---

## 目标
Set up Pomelli Business DNA for WorldGlasses and generate initial campaign assets (5 Instagram posts + 3 Facebook ads + 2 Reels/TikTok videos)

## 约束
- Input: WorldGlasses website (oyster/products/worldglasses-web/)
- Use labs.google.com/pomelli for brand DNA extraction
- Use Pomelli Animate for video generation
- Output directory: oyster/media/pomelli/worldglasses/
- Brand positioning: AR/AI-powered smart glasses for enterprise
- No hardcoding brand copy; use Pomelli outputs only

## 验收标准
- [ ] Pomelli brand DNA JSON saved to docs/pomelli/brand-dna-worldglasses.json
- [ ] 5 Instagram posts generated (captions + image descriptions)
- [ ] 3 Facebook ads generated (copy + design specs)
- [ ] 2 short-form videos generated (Reels/TikTok format, <60s each)
- [ ] All assets organized in oyster/media/pomelli/worldglasses/ subdirs:
  - instagram_posts/
  - facebook_ads/
  - videos/
- [ ] JSON manifest saved listing all generated assets

## 不要做
- Don't modify WorldGlasses website or product pages
- Don't use hardcoded copy; extract from Pomelli API only
- Don't upload to social platforms yet
