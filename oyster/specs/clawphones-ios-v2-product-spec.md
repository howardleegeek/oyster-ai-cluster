# ClawPhones iOS v2 产品 Spec

> **Author:** Opus (总指挥)
> **Date:** 2026-02-10
> **Executor:** Codex (分批实现)
> **Repo:** `~/.openclaw/workspace/` (github: howardleegeek/openclaw-mobile)

---

## 现状

iOS app 目前只有：
- 粘贴 token → 进入聊天列表 → 发消息 → 收回复
- 没有用户系统、没有设置、没有 AI 自定义、没有计划管理
- 后端 proxy (server.py) 只有 device_token 概念，没有 user 概念

---

## 目标架构

```
┌──────────────────────────────────────────────┐
│  iOS App                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ 登录/注册 │ │ 聊天界面  │ │ 设置 (我的)   │ │
│  │          │ │ (现有)    │ │ 计划/AI/账号  │ │
│  └──────────┘ └──────────┘ └──────────────┘ │
└──────────────────┬───────────────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────────────┐
│  后端 API (server.py on EC2)                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │
│  │ Auth   │ │ User   │ │ Chat   │ │ Plan  │ │
│  │ API    │ │ API    │ │ API    │ │ API   │ │
│  └────────┘ └────────┘ └────────┘ └───────┘ │
│                    │                          │
│              SQLite DB                        │
│  (users, plans, ai_configs, conversations)   │
└──────────────────┬───────────────────────────┘
                   │
          OpenRouter (Kimi/DeepSeek/Claude)
```

---

## Phase 1: 用户登录/注册 (P0)

### 后端 API

#### POST /v1/auth/register
```json
// Request
{
  "email": "user@example.com",
  "password": "xxx",
  "name": "Howard"  // optional
}
// Response 201
{
  "user_id": "uuid",
  "token": "ocw1_xxx",
  "tier": "free",
  "created_at": 1234567890
}
```

#### POST /v1/auth/login
```json
// Request
{
  "email": "user@example.com",
  "password": "xxx"
}
// Response 200
{
  "user_id": "uuid",
  "token": "ocw1_xxx",
  "tier": "pro",
  "name": "Howard",
  "ai_config": { ... }
}
```

#### POST /v1/auth/login/apple
```json
// Request
{
  "identity_token": "xxx",  // Apple Sign In JWT
  "name": "Howard"  // first time only
}
// Response 200 (same as login)
```

### DB Schema (新增 users 表)
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  apple_id TEXT UNIQUE,
  name TEXT,
  avatar_url TEXT,
  tier TEXT DEFAULT 'free',
  ai_config TEXT DEFAULT '{}',  -- JSON
  language TEXT DEFAULT 'auto',
  created_at INTEGER,
  updated_at INTEGER
);

-- 现有 device_tokens 表加 user_id 字段
ALTER TABLE device_tokens ADD COLUMN user_id TEXT REFERENCES users(id);
```

### iOS UI

#### LoginView (新页面)
- 邮箱 + 密码输入
- "注册" / "登录" 切换
- "Sign in with Apple" 按钮
- 登录成功 → 存 token 到 Keychain → 进入主页
- 替换现有的 SetupView（粘贴 token 保留为开发者后门）

#### 导航变更
```
App Launch
  ├─ 有 token → ConversationListView (不变)
  └─ 无 token → LoginView (替换 SetupView)
```

### 验收标准
- [ ] 用邮箱注册 → 自动登录 → 进入聊天
- [ ] 邮箱登录成功
- [ ] Apple Sign In 成功
- [ ] 重复邮箱注册返回 409
- [ ] 密码错误返回 401
- [ ] Token 持久化，重启 app 不需要重新登录

---

## Phase 2: 用户设置 (P0)

### 后端 API

#### GET /v1/user/profile
```json
// Response
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Howard",
  "avatar_url": null,
  "tier": "free",
  "language": "auto",
  "created_at": 1234567890
}
```

#### PUT /v1/user/profile
```json
// Request (partial update)
{
  "name": "Howard Lee",
  "language": "zh"
}
// Response 200 (updated profile)
```

#### PUT /v1/user/password
```json
{
  "old_password": "xxx",
  "new_password": "yyy"
}
```

### iOS UI

#### SettingsView (新 Tab 或导航项)
```
我的
├─ 头像 + 昵称 (可编辑)
├─ 邮箱 (只读)
├─ 语言设置 (自动/中文/English)
├─ 当前计划 → PlanView
├─ AI 设置 → AIConfigView
├─ 修改密码
├─ 清除所有对话
└─ 退出登录
```

### 验收标准
- [ ] 修改昵称成功
- [ ] 修改语言 → AI 回复语言跟着变
- [ ] 退出登录 → 清除 Keychain → 回到 LoginView
- [ ] 修改密码成功

---

## Phase 3: 用户计划 (P1)

### 后端 API

#### GET /v1/user/plan
```json
{
  "tier": "free",
  "limits": {
    "messages_per_day": 50,
    "model": "deepseek-chat",
    "features": ["basic_chat"]
  },
  "usage": {
    "messages_today": 12,
    "messages_total": 156
  },
  "available_plans": [
    {
      "tier": "free",
      "price": 0,
      "model": "DeepSeek",
      "messages_per_day": 50,
      "features": ["basic_chat"]
    },
    {
      "tier": "pro",
      "price": 9.99,
      "model": "Kimi K2.5",
      "messages_per_day": 500,
      "features": ["basic_chat", "web_search", "long_context"]
    },
    {
      "tier": "max",
      "price": 29.99,
      "model": "Claude Sonnet 4",
      "messages_per_day": -1,
      "features": ["basic_chat", "web_search", "long_context", "tools", "vision"]
    }
  ]
}
```

#### POST /v1/user/plan/upgrade
```json
// Request
{ "tier": "pro" }
// Response (暂时直接升级，后续接支付)
{ "tier": "pro", "effective_at": 1234567890 }
```

### iOS UI

#### PlanView (新页面)
```
当前计划: Free
每日消息: 12/50
模型: DeepSeek

[升级到 Pro - ¥69/月]
  · Kimi K2.5 模型
  · 每日 500 条消息
  · 联网搜索
  · 长上下文记忆

[升级到 Max - ¥199/月]
  · Claude Sonnet 4 模型
  · 无限消息
  · 全部功能
```

### 验收标准
- [ ] 看到当前计划和用量
- [ ] 看到可升级的计划列表
- [ ] 点升级 → 计划变更 → 聊天模型自动切换
- [ ] 用量到限额 → 提示升级

---

## Phase 4: AI 个性化设置 (P1)

### 后端 API

#### GET /v1/user/ai-config
```json
{
  "persona": "assistant",
  "custom_prompt": "",
  "temperature": 0.7,
  "available_personas": [
    {
      "id": "assistant",
      "name": "通用助手",
      "description": "聪明友好的 AI 助手",
      "icon": "brain"
    },
    {
      "id": "coder",
      "name": "编程专家",
      "description": "精通各种编程语言",
      "icon": "chevron.left.forwardslash.chevron.right"
    },
    {
      "id": "writer",
      "name": "写作助手",
      "description": "帮你写文章、邮件、文案",
      "icon": "pencil"
    },
    {
      "id": "translator",
      "name": "翻译官",
      "description": "中英日韩多语言互译",
      "icon": "globe"
    },
    {
      "id": "custom",
      "name": "自定义",
      "description": "完全自定义 AI 行为",
      "icon": "slider.horizontal.3"
    }
  ]
}
```

#### PUT /v1/user/ai-config
```json
{
  "persona": "coder",
  "custom_prompt": "你精通 Swift 和 Python",
  "temperature": 0.5
}
```

### iOS UI

#### AIConfigView (新页面)
```
AI 人设
├─ 🧠 通用助手 (当前) ✓
├─ 💻 编程专家
├─ ✍️ 写作助手
├─ 🌍 翻译官
└─ ⚙️ 自定义

[自定义提示词]
(多行输入框, 最多 500 字)

回复风格
[简洁] ─────●── [详细]
```

### 后端逻辑变更 (server.py)
chat 时自动拼接 system prompt:
```python
system_prompt = get_persona_prompt(user.ai_config.persona)
if user.ai_config.custom_prompt:
    system_prompt += "\n" + user.ai_config.custom_prompt
# 插入到 messages[0] 作为 system role
```

### 验收标准
- [ ] 选择预设人设 → AI 回复风格变化
- [ ] 自定义提示词 → 生效
- [ ] 调整 temperature → 回复随机度变化
- [ ] 设置持久化，重启 app 保留

---

## Phase 5: 聊天体验优化 (P1)

### 5a. 流式回复 (SSE)

#### 后端
- 新增 `POST /v1/conversations/{id}/chat/stream`
- 返回 `text/event-stream`
- 每个 chunk: `data: {"delta":"你","done":false}\n\n`
- 最后: `data: {"delta":"","done":true,"message_id":"uuid"}\n\n`

#### iOS
- 用 `URLSession` 的 `bytes(for:)` 逐行读取 SSE
- 逐字追加到 assistant message
- 自动滚动跟随

### 5b. Markdown 渲染
- 用系统自带 `Text(AttributedString(markdown:))` 或第三方库
- 支持: 粗体、斜体、代码块、链接、列表

### 5c. 消息交互
- 长按消息 → 复制/分享/重新生成
- 向左滑消息 → 删除单条
- "正在思考..." 动画 (三个跳动的点)

### 验收标准
- [ ] 流式回复逐字显示
- [ ] Markdown 正确渲染
- [ ] 长按复制成功
- [ ] 重新生成功能正常

---

## 实施计划

### 批次安排 (Codex Tasks)

| 批次 | 任务 | 依赖 | 预估时间 |
|------|------|------|---------|
| **C10** | 后端 users 表 + auth API (register/login/apple) | 无 | 2h |
| **C11** | iOS LoginView + Apple Sign In | C10 | 2h |
| **C12** | 后端 profile + password API | C10 | 1h |
| **C13** | iOS SettingsView (全部设置页面) | C11, C12 | 2h |
| **C14** | 后端 plan API + usage tracking | C10 | 1.5h |
| **C15** | iOS PlanView (计划展示 + 升级) | C13, C14 | 1.5h |
| **C16** | 后端 ai-config API + persona prompts | C10 | 1.5h |
| **C17** | iOS AIConfigView | C13, C16 | 1.5h |
| **C18** | 后端 SSE streaming endpoint | 无 | 2h |
| **C19** | iOS 流式回复 + Markdown 渲染 | C18 | 2h |
| **C20** | iOS 消息交互 (复制/删除/重新生成) | 无 | 1h |

### 并行策略
```
Wave 1 (并行): C10 + C18
Wave 2 (并行): C11 + C12 + C16
Wave 3 (并行): C13 + C14 + C17 + C19
Wave 4 (并行): C15 + C20
```

### 文件影响

| 文件 | 改动类型 |
|------|---------|
| `proxy/server.py` | 大改 — 加 auth, user, plan, ai-config, SSE |
| `ios/Services/OpenClawAPI.swift` | 大改 — 加 auth, user, plan, ai-config, SSE |
| `ios/Views/LoginView.swift` | 新建 |
| `ios/Views/SettingsView.swift` | 新建 |
| `ios/Views/PlanView.swift` | 新建 |
| `ios/Views/AIConfigView.swift` | 新建 |
| `ios/Views/MessageRow.swift` | 改 — Markdown 渲染 |
| `ios/Views/ChatView.swift` | 改 — 流式、长按菜单 |
| `ios/ViewModels/ChatViewModel.swift` | 改 — SSE 逻辑 |
| `ios/ViewModels/AuthViewModel.swift` | 新建 |
| `ios/ViewModels/SettingsViewModel.swift` | 新建 |
| `ios/App/ContentView.swift` | 改 — 导航结构 |

---

## 注意事项

1. **密码存储**: 用 bcrypt hash, 绝不明文
2. **Apple Sign In**: 需要 Apple Developer Account 的 Sign In with Apple capability
3. **支付**: Phase 3 暂时不接真实支付，admin 手动升级 tier。后续接 Stripe 或 Apple IAP
4. **迁移**: 现有 device_token 用户需要平滑迁移 — 保留 token 登录作为降级方案
5. **Rate Limit**: 免费用户 50 条/天，需要在 server.py 里加计数器
