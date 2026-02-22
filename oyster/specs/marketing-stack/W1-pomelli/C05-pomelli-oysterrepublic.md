---
task_id: C05-pomelli-oysterrepublic
project: marketing-stack
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["docs/pomelli/brand-dna-oysterrepublic.json"]
executor: glm
---

## 目标
Set up Pomelli Business DNA for Oyster Republic and generate initial campaign assets (5 Instagram posts + 3 Facebook ads + 2 Reels/TikTok videos)

## 约束
- Input: Oyster Republic documentation/brand materials (oyster/products/ or ecosystem docs)
- Use labs.google.com/pomelli for brand DNA extraction
- Use Pomelli Animate for video generation
- Output directory: oyster/media/pomelli/oysterrepublic/
- Brand positioning: Decentralized community and ecosystem nation
- No hardcoding brand copy; use Pomelli outputs only

## 验收标准
- [ ] Pomelli brand DNA JSON saved to docs/pomelli/brand-dna-oysterrepublic.json
- [ ] 5 Instagram posts generated (captions + image descriptions)
- [ ] 3 Facebook ads generated (copy + design specs)
- [ ] 2 short-form videos generated (Reels/TikTok format, <60s each)
- [ ] All assets organized in oyster/media/pomelli/oysterrepublic/ subdirs:
  - instagram_posts/
  - facebook_ads/
  - videos/
- [ ] JSON manifest saved listing all generated assets

## 不要做
- Don't modify Oyster Republic documentation or brand materials
- Don't use hardcoded copy; extract from Pomelli API only
- Don't upload to social platforms yet
