# Twitter + 营销优化 Spec — GLM Vision 全面集成

> **Author**: Opus (战略 spec)
> **Date**: 2026-02-11
> **Status**: Phase 1 DONE → 待 dispatch
> **执行**: GLM 节点并发

---

## 背景

Twitter 自动化系统已有 3 个核心模块：
- `twitter_poster.py` (3280 行) — 发帖引擎，5 种后端
- `engagement_farmer.py` (2287 行) — 自动 engagement，54 条/天
- `ui_agent.py` (1390 行) — 视觉 fallback，5 个 LLM 后端

**问题**: GLM Vision 目前仅作为 selector 失败后的 fallback，没有主动用于内容质量提升和营销分析。

**目标**: 将 GLM Vision 从被动 fallback 升级为主动参与的营销智能层。

---

## 四大模块

### Module A: 发帖流程增强 (twitter_poster.py)

**A1: 发帖前预览检查 (Pre-Post Vision Check)**

文件: `twitter_poster.py` — 在 `post_cdp()` 函数中，compose 完成、点 Post 之前插入检查。

```python
# 位置: post_cdp() 函数，在 click "Post" button 之前
async def _vision_pre_check(page, text: str, agent: UIAgent) -> dict:
    """
    发帖前截图分析:
    - 内容是否正确渲染（换行、emoji、链接预览）
    - 是否有拼写/格式错误的视觉线索
    - 图片/视频预览是否正常加载
    - compose 框是否还有残留草稿
    返回: {"ok": bool, "issues": [str], "screenshot_path": str}
    """
```

要求:
1. 在 compose 填完文本后、点 Post 前调用
2. 截图 → 发给 GLM Vision 分析
3. 如果发现问题（如文本被截断、图片未加载），自动等待/重试
4. 问题严重（错误账号、内容为空）→ 中止发帖，记录到 log
5. 轻微问题（格式微调）→ 记录 warning 但继续发帖
6. 新增 `--skip-vision-check` CLI flag 跳过检查（性能模式）
7. 记录检查结果到 `~/.twitter-poster/vision_checks.log`

**A2: 图片质量分析 (Image Quality Gate)**

文件: `twitter_poster.py` — 新增函数，在带图发帖前调用。

```python
async def _check_image_quality(image_path: str, agent: UIAgent) -> dict:
    """
    图片质量门控:
    - 分辨率是否够 (≥600px 宽)
    - 是否模糊/过暗/过亮
    - 文字是否可读 (如果有文字)
    - 是否包含敏感内容标志
    - Twitter 裁剪后关键内容是否被切掉 (16:9 和 1:1 预览)
    返回: {"quality_score": float 0-1, "issues": [str], "recommendation": str}
    """
```

要求:
1. 对 `--image` 参数的图片，上传前分析
2. quality_score < 0.5 → 警告但继续（记录 log）
3. quality_score < 0.2 → 中止，建议换图
4. 预测 Twitter 裁剪位置，检查关键内容是否在安全区域内

**A3: 发帖后验证增强 (Post-Publish Verification)**

文件: `twitter_poster.py` — 增强现有的发帖成功验证。

当前: 只检查 URL 是否返回。
增强: 截图验证发帖后的推文外观。

```python
async def _vision_post_verify(page, expected_text: str, agent: UIAgent) -> dict:
    """
    发帖后验证:
    - 推文是否真的出现在 timeline
    - 内容是否与预期一致
    - 是否被 Twitter 折叠/限流（"This post may violate..."）
    - 互动按钮是否正常（reply/retweet/like 可点击）
    返回: {"verified": bool, "visible": bool, "flagged": bool}
    """
```

---

### Module B: Engagement 增强 (engagement_farmer.py)

**B1: 目标推文视觉分析**

文件: `engagement_farmer.py` — 增强 `_analyze_tweet_for_reply()` 或等价函数。

当前: 只分析推文文本 → 生成回复。
增强: 截图分析推文的图片/视频缩略图/引用推文，生成更精准的回复。

```python
async def _vision_analyze_tweet(page, tweet_element, agent: UIAgent) -> dict:
    """
    视觉分析目标推文:
    - 推文是否包含图片/视频 → 描述内容
    - 是否是引用推文 → 理解完整上下文
    - 推文互动数据视觉读取（likes/retweets/views 数字）
    - 推文作者 profile 分析（头像、bio、follower 数）
    返回: {"has_media": bool, "media_description": str,
            "engagement_level": str, "author_profile": dict,
            "full_context": str}
    """
```

要求:
1. 在搜索结果页，对每个候选推文截图分析
2. 有图/视频的推文 → 把视觉描述加入 Grok 的回复生成 prompt
3. 高互动推文优先回复（视觉读取 engagement 数字）
4. 识别已回复过的推文（避免重复）
5. 结果缓存到 `~/.twitter-poster/tweet_analysis_cache/`，同一推文不重复分析

**B2: 回复质量视觉验证**

文件: `engagement_farmer.py` — 发送回复后的验证。

```python
async def _verify_reply_posted(page, reply_text: str, agent: UIAgent) -> dict:
    """
    验证回复是否成功:
    - 回复是否出现在推文下方
    - 是否被折叠/隐藏
    - 回复内容是否完整（未被截断）
    返回: {"success": bool, "visible": bool, "folded": bool}
    """
```

**B3: 人设一致性检查**

```python
async def _check_persona_consistency(reply_text: str, account_handle: str,
                                       recent_replies: list, agent: UIAgent) -> dict:
    """
    检查回复是否符合账号人设:
    - 语气是否与账号定位一致
    - 是否重复了近期的回复模式
    - 多样性评分
    返回: {"consistent": bool, "diversity_score": float, "suggestions": [str]}
    """
```

注意: 这个用文本分析就够，不需要 Vision。用 GLM 文本能力 (通过 z.ai API) 而非 Vision。

---

### Module C: 营销数据分析 (新文件: marketing_analyzer.py)

**C1: Twitter Analytics 截图分析**

新文件: `marketing_analyzer.py`

```python
class MarketingAnalyzer:
    """
    定期截图分析 Twitter Analytics 页面，生成营销报告。
    运行方式: cron job 或手动调用。

    功能:
    1. analytics_snapshot() — 截图 Analytics dashboard → 提取关键指标
    2. competitor_analysis() — 截图竞品账号 → 分析策略
    3. trend_detection() — 截图 Explore/Trending → 发现机会
    4. content_performance() — 分析最近推文的表现数据
    """
```

**C1a: Analytics Snapshot**

```python
async def analytics_snapshot(self, account: str) -> dict:
    """
    步骤:
    1. CDP 连接 → 导航到 analytics.twitter.com (或 x.com/HANDLE/analytics)
    2. 截图 overview dashboard
    3. GLM Vision 提取: impressions, engagements, followers 变化, top tweet
    4. 与上次快照对比 → 计算增长率
    5. 存储到 ~/.twitter-poster/analytics/YYYYMMDD-HANDLE.json
    返回: {"impressions": int, "engagements": int, "followers": int,
            "growth": {"impressions_delta": float, ...}, "top_tweets": []}
    """
```

**C1b: 竞品分析**

```python
async def competitor_analysis(self, competitors: list[str]) -> dict:
    """
    竞品账号列表 (配置在 accounts.json 或单独文件):
    - @Meta, @rayaboreal (AR glasses)
    - @soaboreal (DePIN)
    - 等

    步骤:
    1. 导航到每个竞品 profile
    2. 截图 → 提取: follower count, 最近发帖频率, 内容类型, 互动率
    3. 与我方账号对比
    4. 生成竞争分析报告
    存储: ~/.twitter-poster/competitor_reports/YYYYMMDD.json
    """
```

**C1c: 趋势发现**

```python
async def trend_detection(self) -> dict:
    """
    1. 导航到 x.com/explore
    2. 截图 trending topics
    3. GLM Vision 提取热门话题列表
    4. 匹配与我们相关的话题 (AI, DePIN, crypto, wearable, glasses)
    5. 如果有匹配 → 自动 enqueue 相关内容到发帖队列
    存储: ~/.twitter-poster/trends/YYYYMMDD.json
    """
```

**C1d: 内容表现分析**

```python
async def content_performance(self, account: str, days: int = 7) -> dict:
    """
    1. 导航到账号 profile
    2. 滚动截图最近 N 天的推文
    3. GLM Vision 提取每条推文的: 文本摘要, likes, retweets, replies, views
    4. 分类: 哪类内容表现好？图片 vs 纯文字？话题分布？
    5. 生成内容策略建议
    存储: ~/.twitter-poster/performance/YYYYMMDD-HANDLE.json
    """
```

---

### Module D: 自动化调度 (新增 cron/launchd)

**D1: 日报生成**

```python
# 在 marketing_analyzer.py 中
async def daily_report(self) -> str:
    """
    汇总当天所有数据:
    - 各账号发帖量 + engagement 量
    - Analytics 关键指标变化
    - 竞品动态
    - 趋势匹配
    - 内容表现排名
    - 建议明天的内容策略
    输出: Markdown 报告 → ~/.twitter-poster/daily_reports/YYYYMMDD.md
    """
```

**D2: launchd 定时任务**

```
com.oyster.twitter-analytics    — 每 6h 跑 analytics_snapshot
com.oyster.twitter-competitors  — 每天 1 次跑 competitor_analysis
com.oyster.twitter-trends       — 每 4h 跑 trend_detection
com.oyster.twitter-performance  — 每天 1 次跑 content_performance
com.oyster.twitter-daily-report — 每天 23:00 跑 daily_report
```

所有 launchd 任务跑在 **Mac-2** (有 Chrome CDP)。

---

## 技术要求

### GLM Vision 调用方式

所有 Vision 调用通过现有 `ui_agent.py` 的 `GLMVisionUIAgent`：

```python
from ui_agent import create_ui_agent_from_env

agent = create_ui_agent_from_env()
# agent 自动选择 GLM Vision (优先级最高)

# 截图 → 分析
screenshot_b64 = await page.screenshot(type="jpeg", quality=70)
result = await agent.analyze(screenshot_b64, prompt="分析这个推文的互动数据...")
```

### 错误处理
- GLM Vision API 失败 → fallback 到 OpenAI Vision (已有链路)
- CDP 断连 → 重试 1 次，失败记录 log 跳过
- 截图太大 → JPEG quality 降到 50%
- 分析超时 (>30s) → 跳过 Vision 检查，继续原流程

### 安全要求
- 不存储完整截图（分析完即删，除非 debug 模式）
- 竞品分析频率限制（每天最多 1 次/竞品）
- 不在公开回复中泄露竞品分析数据
- 所有 API key 从环境变量读取

### 文件结构
```
twitter-poster/
├── twitter_poster.py     (修改: +A1, +A2, +A3)
├── engagement_farmer.py  (修改: +B1, +B2, +B3)
├── ui_agent.py           (不改，现有 GLM Vision 能力足够)
├── marketing_analyzer.py (新建: C1a-d, D1)
├── competitors.json      (新建: 竞品列表配置)
└── launchd/
    ├── com.oyster.twitter-analytics.plist     (D2)
    ├── com.oyster.twitter-competitors.plist   (D2)
    ├── com.oyster.twitter-trends.plist        (D2)
    ├── com.oyster.twitter-performance.plist   (D2)
    └── com.oyster.twitter-daily-report.plist  (D2)
```

---

## 执行计划 (并发 dispatch)

### Wave 1 (并发 3 任务)

| Task | 模块 | 文件 | 节点 | 预估 |
|------|------|------|------|------|
| T1 | A1+A2+A3 | twitter_poster.py | GCP codex-node-1 | 20 min |
| T2 | B1+B2+B3 | engagement_farmer.py | GCP glm-node-2 | 20 min |
| T3 | C1a-d + D1 | marketing_analyzer.py (新) | GCP codex-node-1 | 25 min |

### Wave 2 (Wave 1 完成后)

| Task | 模块 | 文件 | 节点 |
|------|------|------|------|
| T4 | D2 | launchd plists (5 个) | Mac-2 本地 |
| T5 | 集成测试 | 全部模块 dry-run | Mac-2 |

### 验收标准
- [ ] A1: 发帖前截图检查可工作，`--skip-vision-check` 跳过
- [ ] A2: 图片质量分析返回 score
- [ ] A3: 发帖后截图验证折叠/限流
- [ ] B1: 推文视觉分析生成 media_description
- [ ] B2: 回复验证可检测折叠
- [ ] B3: 人设一致性评分
- [ ] C1: marketing_analyzer.py 4 个功能可运行
- [ ] D1: 日报生成 Markdown
- [ ] D2: 5 个 launchd plist 正确
- [ ] 全部代码无 hardcoded key
- [ ] 错误处理: Vision 失败时 graceful fallback
