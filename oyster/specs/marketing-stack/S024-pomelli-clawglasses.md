---
task_id: S024-pomelli-clawglasses
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["docs/pomelli/brand-dna-clawglasses.json"]
executor: glm
---

## 目标
Set up Pomelli Business DNA for ClawGlasses and generate initial campaign assets (5 Instagram posts + 3 Facebook ads + 2 Reels/TikTok videos)

## 约束
- Input: ClawGlasses website (oyster/products/clawglasses/ or similar)
- Use labs.google.com/pomelli for brand DNA extraction
- Use Pomelli Animate for video generation
- Output directory: oyster/media/pomelli/clawglasses/
- Brand positioning: AI-powered smart glasses hardware
- No hardcoding brand copy; use Pomelli outputs only

## 验收标准
- [ ] Pomelli brand DNA JSON saved to docs/pomelli/brand-dna-clawglasses.json
- [ ] 5 Instagram posts generated (captions + image descriptions)
- [ ] 3 Facebook ads generated (copy + design specs)
- [ ] 2 short-form videos generated (Reels/TikTok format, <60s each)
- [ ] All assets organized in oyster/media/pomelli/clawglasses/ subdirs:
  - instagram_posts/
  - facebook_ads/
  - videos/
- [ ] JSON manifest saved listing all generated assets

## 不要做
- Don't modify ClawGlasses website or product pages
- Don't use hardcoded copy; extract from Pomelli API only
- Don't upload to social platforms yet
