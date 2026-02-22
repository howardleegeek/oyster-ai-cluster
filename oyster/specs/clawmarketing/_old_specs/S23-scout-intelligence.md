---
task_id: S23-scout-intelligence
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
Build Scout Agent intelligence system for ClawMarketing - real-time market intelligence gathering using existing Playwright.

## 约束
- Use existing Playwright (already installed in project)
- API-first approach: use Twitter API, Reddit API where available
- Fallback to Playwright for websites without API
- Use Jina Reader / Firecrawl for LLM-friendly scraping
- Data source whitelist: user-configurable
- Do NOT hard-scrape LinkedIn/Twitter (use official APIs only)

## 具体改动
1. Create backend/agents/scout_agent.py:
   - ScoutAgent class
   - gather_intelligence(keywords, sources) method
   - monitor_competitors(competitor_list) method
   - extract_sentiment(platform, topic) method
   
2. Create backend/routers/scout.py:
   - POST /api/v1/scout/gather - gather intelligence on keywords
   - POST /api/v1/scout/monitor - start monitoring competitors
   - GET /api/v1/scout/feed - get intelligence feed
   - GET /api/v1/scout/sentiment - get sentiment analysis

3. Create Scout's "炼金术" (data processing):
   - DataCleaner class: remove ads, noise
   - SentimentCluster class: group similar complaints
   - InsightExtractor class: extract actionable insights

4. Add data source whitelist model:
   - User config: 5 competitor sites + 3 industry forums
   - Store in existing database

5. Register scout router in backend/main.py

## 技术方案 (Playwright优先 + 免费API)
- **Playwright主战**: 行业博客、竞品新闻页、论坛、Reddit评论、LinkedIn动态
- **免费API**: 
  - Reddit API (免费Tier)
  - Hacker News API (免费)
  - Google News RSS (免费)
  - DuckDuckGo (免费搜索)
- **Jina Reader**: 将网页转为Markdown供LLM处理

## 数据源 (免费 + Playwright可爬)
- Reddit (r/、search)
- Hacker News
- 行业论坛 (可配置白名单)
- 竞品官网/Blog (Playwright)
- Google News RSS

## 验收标准
- [ ] scout_agent.py exists with core methods
- [ ] /api/v1/scout/gather endpoint returns intelligence data
- [ ] /api/v1/scout/feed returns formatted insights
- [ ] Sentiment analysis works on sample data
- [ ] Data source whitelist is configurable

## 不要做
- Don't hard-scrape LinkedIn/Twitter without API
- Don't store PII
- Don't modify existing agents
