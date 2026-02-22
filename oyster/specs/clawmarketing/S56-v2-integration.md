---
task_id: S56-clawmarketing-v2-features
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - frontend/src/pages/*.tsx
  - backend/main.py
---

## 目标
实现 ClawMarketing V2 功能迭代，集成 GLM AI 能力

## 约束
- 不改 UI/CSS 架构
- 不加新依赖
- 使用现有的 GLM API (/api/v2/chat)

## 具体改动

### 已完成的后端 API (V1-V30)
确保以下 API 正常工作：
- /api/v2/chat - GLM 聊天
- /api/v2/content/generate - AI 生成内容
- /api/v2/content/{id}/publish - 发布内容
- /api/v2/analytics/* - 分析
- /api/v2/personas/* - Persona
- /api/v2/campaigns/* - 战役
- /api/v2/content/calendar - 日历
- /api/v2/content/suggest - AI 建议
- /api/v2/content/hashtags - Hashtag
- /api/v2/content/seo-score - SEO
- /api/v2/trending - 热门话题
- /api/v2/audience - 受众洞察

### 前端页面集成

1. **Home.tsx (AI 助手)**
   - 连接 /api/v2/chat
   - 连接 /api/v2/content/generate
   - 显示生成的内容卡片

2. **Dashboard.tsx (作战室)**
   - 显示真实 API 数据
   - 战役选择器 → /api/v2/campaigns/
   - 内容统计 → /api/v2/analytics/summary
   - Persona 矩阵 → /api/v2/personas/

3. **Content.tsx (内容管理)**
   - 连接 /api/v2/content/ 获取真实数据
   - 发布按钮 → /api/v2/content/{id}/publish
   - 审核按钮 → /api/v2/content/{id}/approve

4. **Campaigns.tsx (战役)**
   - 连接 /api/v2/campaigns/
   - 真实 CRUD 操作

5. **Analytics.tsx (分析)**
   - 连接 /api/v2/analytics/summary
   - 连接 /api/v2/analytics/content
   - 连接 /api/v2/trending

## 验收标准
- [ ] 前端所有页面数据来自真实 API
- [ ] AI 助手可以生成内容并保存
- [ ] 内容可以发布状态流转
- [ ] Dashboard 显示真实统计
- [ ] 无 JS 错误

## 验证命令
```bash
# 测试 API
curl -s http://localhost:8001/api/v2/chat -X POST -d '{"messages":[{"role":"user","content":"hello"}]}'

# 测试前端
cd frontend && npm run build
```
