# 拜占庭对撞器 (Byzantine Collider)

> AI-to-AI 产品碰撞系统 — 用集群算力对撞出想法

## v1.3 完整版

| 功能 | 状态 |
|------|------|
| 三阶段闭环 | ✅ |
| 6+2 种 Prompt 模板 | ✅ |
| LLM 多模型支持 | ✅ |
| REST API | ✅ |
| Web UI (移动端+主题) | ✅ |
| Webhook | ✅ |
| Dispatch 集成 | ✅ |
| Docker | ✅ |
| SQLite 持久化 | ✅ |
| 报告自动生成 | ✅ |
| Telegram Bot | ✅ |
| Discord 通知 | ✅ |
| 定时任务 | ✅ |
| 单元测试 | ✅ |
| ai_os 自动同步 | ✅ |

---

## 快速启动

```bash
# Docker (推荐)
cp .env.example .env
docker-compose up -d

# 直接运行
pip install -r requirements.txt
python3 api.py
```

---

## 目录结构

```
byzantine-collider/
├── byzantine_collider.py      # 碰撞核心
├── research.py                # 网络调研
├── llm.py                    # LLM 适配
├── api.py                    # REST API + Web UI
├── storage.py                # SQLite 持久化
├── notify.py                 # 通知模块
├── reporter.py              # 报告生成 ✨新
├── ai_os_sync.py            # ai_os 同步 ✨新
├── telegram_bot.py          # Telegram Bot ✨新
├── scheduler.py             # 定时任务 ✨新
├── dispatch_integration.py   # Dispatch 集成
├── test_byzantine.py        # 单元测试 ✨新
├── web/index.html           # Web UI
├── Dockerfile               # Docker
├── docker-compose.yml       # Compose
├── requirements.txt
└── README.md
```

---

## 接口

| 接口 | 功能 |
|------|------|
| `GET /` | Web UI |
| `GET /health` | 健康检查 |
| `POST /api/collision` | 发起碰撞 |
| `GET /api/collision/:id` | 获取结果 |
| `POST /api/research` | 网络调研 |
| `POST /webhook` | Webhook 回调 |

---

## 定时任务

```bash
python3 scheduler.py
```

- 每日 09:00: 每日报告
- 每日 23:00: 同步到 ai_os
- 每小时: 健康检查
- 每周一 10:00: 周报摘要

---

## Telegram Bot 命令

- `/start` - 启动
- `/碰撞 [主题]` - 发起碰撞
- `/结果 [id]` - 查看结果
- `/状态` - API 状态
- `/帮助` - 帮助

---

## 版本历史

- **v1.3** (当前) - 完整版
- **v1.2** - Web UI + API + Webhook
- **v1.1** - LLM 多模型支持
- **v1.0** - 基础三阶段闭环
