---
task_id: S03-product-social-scan
project: open-source-research
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["research/product-social-scan.md"]
executor: codex
---

## 目标
搜索 GitHub 上最佳的产品/社交媒体开源项目，为 Oyster Labs 以下项目找到可直接 Fork 使用的替代方案。

## 搜索清单

1. **营销自动化平台** — 搜索: "marketing automation open source", "hubspot alternative", "mautic erxes"
2. **VoIP 电话系统** — 搜索: "voip phone system open source", "asterisk fonoster", "webrtc phone"
3. **计算机视觉平台** — 搜索: "computer vision platform", "roboflow supervision", "object detection framework"
4. **DevOps 控制面板** — 搜索: "devops dashboard open source", "paas control panel", "caprover coolify"
5. **NFT/数字资产市场** — 搜索: "nft marketplace open source", "digital asset marketplace"
6. **Twitter 自动发帖** — 搜索: "twitter bot python", "twitter auto post", "tweepy automation"
7. **Bluesky 自动化** — 搜索: "bluesky bot", "atproto sdk python", "bluesky automation"
8. **Discord 管理 Bot** — 搜索: "discord admin bot python", "discord moderation bot", "red-discordbot"
9. **LinkedIn 自动化** — 搜索: "linkedin automation python", "linkedin outreach tool"
10. **WhatsApp 自动化** — 搜索: "whatsapp automation", "whatsapp-web.js", "whatsapp bot nodejs"
11. **Reddit 管理** — 搜索: "reddit bot python", "reddit manager tool", "praw automation"
12. **任务控制仪表盘** — 搜索: "mission control dashboard", "nasa openmct", "telemetry dashboard"
13. **AI 学习助手** — 搜索: "ai tutor", "ai study companion", "learning assistant llm"
14. **开源 CRM** — 搜索: "open source crm", "twenty crm", "salesforce alternative"

## 输出格式

```markdown
### [项目名称]

| Repo | Stars | 最后更新 | License | 语言 | 匹配度 | 推荐用法 |
|------|-------|---------|---------|------|--------|---------|
| owner/repo | 数字 | YYYY-MM | 许可证 | 语言 | 高/中/低 | Fork/集成/参考 |

**推荐理由**: ...
**集成方式**: ...
```

## 约束
- Stars > 50，最近 12 个月活跃
- 优先 MIT / Apache-2.0 / BSD
- 每个类别至少 3 个候选
- 社交媒体工具特别注意 API rate limit 和 TOS 合规性

## 验收标准
- [ ] 14 个类别都有结果
- [ ] 每个至少 3 个候选
- [ ] 包含完整元数据
- [ ] 有 API/SDK 集成建议
