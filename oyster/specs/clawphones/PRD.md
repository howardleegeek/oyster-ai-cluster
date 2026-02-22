# ClawPhones PRD - AI 手机助手

> **Version:** 1.0  
> **Date:** 2026-02-14  
> **Project:** ClawPhones  
> **Goal：** 把 ClawBot AI 助手装进手机，分别有 iOS 和 Android 版本

---

## 1. 产品概述

**产品名称：** ClawPhones  
**产品定位：** 个人 AI 助手手机 App  
**目标用户：** Oyster Labs 硬件用户 / 普通消费者  
**核心价值：** 预装 ClawBot AI 助手，零配置即用，语音 + 文字交互  
**变现模式：** 设备绑定销售 / 订阅制

---

## 2. 目标用户

| 用户类型 | 场景 | 需求 |
|----------|------|------|
| Oyster 硬件用户 | Universal Phone、Puffy、ClawGlasses 预装 | 开机即用，无缝体验 |
| 普通用户 | App Store / Play Store 下载 | 快速注册，AI 助手 |
| 企业用户 | 团队协作、AI 助手定制 | API、企业版 |

---

## 3. 核心功能

### 3.1 AI 对话（核心）

| 功能 | 描述 |
|------|------|
| 文字聊天 | 多轮对话，上下文记忆 |
| 语音输入 | 语音转文字（STT） |
| 语音播报 | AI 回复转语音（TTS） |
| 多模态 | 支持图片输入分析 |

### 3.2 ClawBot 能力

基于 OpenClaw / Claude AI：

- 📧 **邮件处理** - 读邮件、写回复
- 📅 **日程管理** - 创建会议、提醒
- 🌐 **网页浏览** - 搜索、研究
- 📁 **文件管理** - 读取、处理文档
- 💬 **社交媒体** - Twitter/Discord 操作
- 🛒 **电商操作** - 下单、追踪物流

### 3.3 设备集成

| 功能 | 描述 |
|------|------|
| 预装 token | 工厂预置设备 token，开机即用 |
| MDM 配置 | 企业设备管理 |
| Siri Shortcuts | iOS 语音助手集成 |
| 推送通知 | 重要事项即时通知 |

### 3.4 账户体系

- 设备绑定（pre-configured token）
- 手机号注册
- WebAuth 登录
- 多设备同步

---

## 4. 技术架构

```
┌─────────────────────────────────────────────────────┐
│              iOS App (SwiftUI)                      │
│         ClawBot / ClawPhones.xcodeproj             │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Chat UI      │  │ Voice (STT)  │                │
│  │ SwiftUI      │  │ SpeechKit    │                │
│  └──────────────┘  └──────────────┘                │
└──────────────────────┬──────────────────────────────┘
                        │
┌──────────────────────▼──────────────────────────────┐
│              Android App (Java/Kotlin)              │
│         ~/android/clawphones-android/              │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Chat UI      │  │ Voice (STT)  │                │
│  │ Jetpack      │  │ TTS Engine   │                │
│  └──────────────┘  └──────────────┘                │
└──────────────────────┬──────────────────────────────┘
                        │
┌──────────────────────▼──────────────────────────────┐
│            OpenClaw Proxy (Backend)                  │
│               api.openclaw.ai                        │
│              ~/proxy/server.py                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ LLM Router   │  │ Conversation │  │ Token Auth │ │
│  │ DeepSeek     │  │ Persistence  │  │ (ocw1_*)   │ │
│  │ Kimi         │  │ SQLite       │  │            │ │
│  │ Claude       │  │              │  │            │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 付费层级

| 层级 | 模型 | 描述 |
|------|------|------|
| Free | DeepSeek | 日常聊天 |
| Pro | Kimi | 长上下文推理 |
| Max | Claude | 最高质量 |

---

## 5. 部署计划

### Phase 1: iOS MVP（2 周）

| 任务 | 状态 |
|------|------|
| SwiftUI 聊天界面 | 待开发 |
| 连接 api.openclaw.ai | 待开发 |
| 设备 token 认证 | 待开发 |
| TestFlight 内部测试 | 待开发 |

### Phase 2: Android MVP（2 周）

| 任务 | 状态 |
|------|------|
| Android 聊天界面 | 待开发 |
| 连接 api.openclaw.ai | 待开发 |
| 设备 token 认证 | 待开发 |
| APK 内测发布 | 待开发 |

### Phase 3: 语音功能（2 周）

| 任务 | 状态 |
|------|------|
| iOS 语音输入（STT） | 待开发 |
| iOS 语音播报（TTS） | 待开发 |
| Android 语音输入 | 待开发 |
| Android 语音播报 | 待开发 |

### Phase 4: App Store 上线（1 周）

| 任务 | 状态 |
|------|------|
| iOS App Store 审核 | 待开发 |
| Google Play 上架 | 待开发 |
| 隐私政策合规 | 待开发 |

---

## 6. 验收标准

### iOS 验收

- [ ] 能聊天（发送文字，收到 AI 回复）
- [ ] 能用预置 token 登录
- [ ] 能创建多个对话
- [ ] 能通过 TestFlight 安装

### Android 验收

- [ ] 能聊天（发送文字，收到 AI 回复）
- [ ] 能用预置 token 登录
- [ ] 能创建多个对话
- [ ] APK 能正常安装

### 完整版验收

- [ ] 语音输入可用
- [ ] 语音播报可用
- [ ] App Store / Play Store 上架
- [ ] 30,000+ 设备部署目标

---

## 7. 域名 / 链接

**App 官网：** `clawphones.com`  
**API：** `api.openclaw.ai`  
**Landing 页：** `~/Downloads/clawphones-landing/`（已存在，可直接部署）

---

## 8. 当前状态

- **iOS：** `~/Downloads/ClawBot-iOS/`（ClawBot 项目，可重命名为 ClawPhones）
- **Android：** `~/.openclaw/workspace/android/clawphones-android/`
- **Backend：** `~/.openclaw/workspace/proxy/server.py`（已存在，API 运行中）
- **Landing：** `~/Downloads/clawphones-landing/`

---

## 9. 待确认

- [ ] ClawBot vs ClawPhones 品牌命名（统一用哪个？）
- [ ] 具体订阅价格
- [ ] 语音功能用哪家 STT/TTS（Google？Apple？自研？）
- [ ] 是否需要离线模式
