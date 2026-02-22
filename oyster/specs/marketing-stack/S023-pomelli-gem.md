---
task_id: S023-pomelli-gem
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["docs/pomelli/brand-dna-gem.json"]
executor: glm
---

## 目标
Set up Pomelli Business DNA for GEM Platform and generate initial campaign assets (5 Instagram posts + 3 Facebook ads + 2 Reels/TikTok videos)

## 约束
- Input: GEM Platform website (oyster/products/gem-platform/)
- Use labs.google.com/pomelli for brand DNA extraction
- Use Pomelli Animate for video generation
- Output directory: oyster/media/pomelli/gem/
- Brand positioning: Web3/DeFi platform for decentralized finance
- No hardcoding brand copy; use Pomelli outputs only

## 验收标准
- [ ] Pomelli brand DNA JSON saved to docs/pomelli/brand-dna-gem.json
- [ ] 5 Instagram posts generated (captions + image descriptions)
- [ ] 3 Facebook ads generated (copy + design specs)
- [ ] 2 short-form videos generated (Reels/TikTok format, <60s each)
- [ ] All assets organized in oyster/media/pomelli/gem/ subdirs:
  - instagram_posts/
  - facebook_ads/
  - videos/
- [ ] JSON manifest saved listing all generated assets

## 不要做
- Don't modify GEM Platform website or product pages
- Don't use hardcoded copy; extract from Pomelli API only
- Don't upload to social platforms yet
