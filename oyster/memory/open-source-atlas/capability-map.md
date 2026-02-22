# Oyster 能力层 → 开源映射数据库

> 任何新需求，先查此表。找到匹配 → Fork/集成。没有匹配 → 才自研。
>
> 最后更新: 2026-02-18

---

## 1. 分布式执行 & 任务调度

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 分布式任务调度 | [ray-project/ray](https://github.com/ray-project/ray) | 37K | Apache-2.0 | 替代 dispatch 60% 功能 |
| 任务队列 | [celery/celery](https://github.com/celery/celery) | 24K | BSD-3 | 分布式任务队列+重试 |
| 工作流编排 | [temporalio/temporal](https://github.com/temporalio/temporal) | 12K | MIT | 替代 lease + 自愈系统 |
| 轻量任务队列 | [rq/rq](https://github.com/rq/rq) | 9.8K | BSD-2 | 简单 Redis 任务队列 |

## 2. AI Agent 框架

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 多 Agent 协作 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | 44K | MIT | 角色分工+任务分配 |
| Agent 图编排 | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 11.7K | MIT | 状态流转图 |
| AI 编码 Agent | [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 65K | MIT | 替代 ai-software-engineering-agent |
| AI 应用平台 | [langgenius/dify](https://github.com/langgenius/dify) | 58K | Apache-2.0 | 内容生成+RAG+工作流 |
| 自进化 Agent | [EvoAgentX/EvoAgentX](https://github.com/EvoAgentX/EvoAgentX) | 2.5K | Apache-2.0 | 自改进 Agent |
| Agent 研究 | [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 16K | Apache-2.0 | Deep Research |

## 3. RAG & 知识系统

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 企业级 RAG | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | 18K | Apache-2.0 | 文档问答管线 |
| 论文问答 | [whitead/paper-qa](https://github.com/whitead/paper-qa) | 6K | Apache-2.0 | 论文检索+问答 |
| 向量数据库 | [qdrant/qdrant](https://github.com/qdrant/qdrant) | 22K | Apache-2.0 | 向量存储 |

## 4. 视觉 & CV

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| CV 工具箱 | [roboflow/supervision](https://github.com/roboflow/supervision) | 36.5K | MIT | 检测+跟踪+标注 |
| 目标检测 | [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) | 38K | AGPL-3.0 | YOLO 实时检测 |
| 人体姿态 | [google/mediapipe](https://github.com/google/mediapipe) | 29K | Apache-2.0 | 手势/人脸/姿态 |
| 边缘推理 | [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 8K | Apache-2.0 | Edge 加速 |
| 眼动追踪 | [pupil-labs/pupil](https://github.com/pupil-labs/pupil) | 4K | LGPL-3.0 | 注意力分析 |

## 5. 边缘 & 设备端 LLM

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 边缘 LLM | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | 95K | MIT | 设备端推理 |
| 移动 LLM | [mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm) | 22K | Apache-2.0 | iOS/Android |
| 浏览器 LLM | [mlc-ai/web-llm](https://github.com/mlc-ai/web-llm) | 17.3K | Apache-2.0 | WebGPU 推理 |
| Prompt 压缩 | [microsoft/LLMLingua](https://github.com/microsoft/LLMLingua) | 5.2K | MIT | 节省 token 成本 |

## 6. Web3 / DeFi / Crypto

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| AMM 引擎 | [Uniswap/v4-core](https://github.com/Uniswap/v4-core) | 2.4K | BUSL-1.1 | Hook 架构自定义 |
| AI 量化交易 | [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 45.9K | GPL-3.0 | ML 策略框架 |
| 金融 LLM | [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) | 18.6K | MIT | DeFi 顾问 |
| DeFi 钱包 | [rainbow-me/rainbow](https://github.com/rainbow-me/rainbow) | 4.1K | GPL-3.0 | 消费级钱包 |
| 预言机 | [smartcontractkit/chainlink](https://github.com/smartcontractkit/chainlink) | 8.2K | MIT | 数据预言机 |
| 保险协议 | [neptune-mutual-blue/protocol](https://github.com/neptune-mutual-blue/protocol) | 579 | BSL-1.1 | 参数化保险 |
| 永续合约 | [drift-labs/protocol-v2](https://github.com/drift-labs/protocol-v2) | 377 | Apache-2.0 | 永续+预测市场 |
| Web3 SDK | [thirdweb-dev/js](https://github.com/thirdweb-dev/js) | 626 | Apache-2.0 | AI + Web3 |
| 去中心化算力 | [akash-network/node](https://github.com/akash-network/node) | 1.1K | Apache-2.0 | 算力市场 |
| ZK 隐私 | [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages) | 417 | Apache-2.0 | 隐私 L2 |

## 7. BFT & 共识

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| BFT 共识 | [cometbft/cometbft](https://github.com/cometbft/cometbft) | 5.7K | Apache-2.0 | Tendermint 继任 |
| Raft 一致性 | [hashicorp/raft](https://github.com/hashicorp/raft) | 8.5K | MPL-2.0 | 轻量共识 |
| P2P 通信 | [libp2p/go-libp2p](https://github.com/libp2p/go-libp2p) | 6K | MIT | 节点发现+通信 |

## 8. 社交媒体自动化

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| Twitter API | [tweepy/tweepy](https://github.com/tweepy/tweepy) | 11.1K | MIT | 发帖+分析 |
| Bluesky SDK | [MarshalX/atproto](https://github.com/MarshalX/atproto) | 639 | MIT | AT Protocol |
| Discord Bot | [Cog-Creators/Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) | 5.4K | GPL-3.0 | 模块化 Bot |
| WhatsApp | [pedroslopez/whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js) | 21.2K | Apache-2.0 | 消息自动化 |
| Reddit | [praw-dev/praw](https://github.com/praw-dev/praw) | 4K | BSD-2 | Reddit API |
| LinkedIn | [eracle/OpenOutreach](https://github.com/eracle/OpenOutreach) | ~100 | MIT | 自动化外联 |
| 社交网络 | [mastodon/mastodon](https://github.com/mastodon/mastodon) | 49.6K | AGPL-3.0 | 去中心化社交 |

## 9. 营销 & 销售

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 营销自动化 | [mautic/mautic](https://github.com/mautic/mautic) | 9.2K | GPL-3.0 | HubSpot 替代 |
| CRM | [twentyhq/twenty](https://github.com/twentyhq/twenty) | 20K | AGPL-3.0 | Salesforce 替代 |
| 竞情分析 | [brightdata/competitive-intelligence](https://github.com/brightdata/competitive-intelligence) | small | - | 多 Agent 竞品分析 |
| AI 爬虫 | [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 58K | Apache-2.0 | LLM 友好爬虫 |

## 10. 语音 & 通信

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 语音 AI Agent | [livekit/agents](https://github.com/livekit/agents) | 9.2K | Apache-2.0 | 实时语音管线 |
| 语音管线 | [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | 5K | BSD-2 | 自定义语音流 |
| 电话引擎 | [asterisk/asterisk](https://github.com/asterisk/asterisk) | 3.1K | GPL-2.0 | VoIP 引擎 |

## 11. Auth & 安全

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 身份管理 | [ory/kratos](https://github.com/ory/kratos) | 11K | Apache-2.0 | Dauth 基础 |
| 认证框架 | [nextauthjs/next-auth](https://github.com/nextauthjs/next-auth) | 25K | ISC | Web Auth |
| WebAuthn | [nicholasgasior/gowasm-webauthn](https://github.com/nicholasgasior/gowasm-webauthn) | small | MIT | 无密码认证 |

## 12. AR 硬件

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 智能眼镜 OS | [AugmentOS-Community/AugmentOS](https://github.com/AugmentOS-Community/AugmentOS) | 1.8K | MIT | 眼镜应用框架 |
| DIY 智能眼镜 | [BasedHardware/OpenGlass](https://github.com/BasedHardware/OpenGlass) | ~1K | MIT | 快速原型 |
| 浏览器 AR | [AR-js-org/AR.js](https://github.com/AR-js-org/AR.js) | 15.8K | MIT | Web AR 演示 |

## 13. 学习 & 教育

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| AI 学习助手 | [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) | 10.3K | MIT | 个性化学习 |
| AI 导师 | [JushBJJ/Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) | 29.7K | - | GPT 提示工程 |

## 14. 法律 & 合同

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 合同审查 | [Open-Source-Legal/OpenContracts](https://github.com/Open-Source-Legal/OpenContracts) | ~400 | AGPL-3.0 | AI 法律文档 |

## 15. 控制面板 & 仪表盘

| 能力 | 开源项目 | Stars | License | 用法 |
|------|---------|-------|---------|------|
| 任务控制台 | [nasa/openmct](https://github.com/nasa/openmct) | 12.8K | Apache-2.0 | NASA 风格仪表盘 |
| PaaS 面板 | [caprover/caprover](https://github.com/caprover/caprover) | 14.8K | Apache-2.0 | DevOps 控制台 |
| NFT 市场 | [reservoirprotocol/marketplace-v2](https://github.com/reservoirprotocol/marketplace-v2) | 164 | MIT | 白标市场 |

---

## 使用指南

### 新项目流程
```
1. 定义需求 → 拆成能力模块
2. 在上面表格中搜索每个能力
3. 如果有匹配 (Stars > 1K, 活跃) → 直接 Fork
4. 如果部分匹配 → Fork + 二次开发
5. 只有在完全没有匹配时才自研
```

### License 风险提醒
- **MIT / Apache-2.0 / BSD**: 安全，随意用
- **GPL / AGPL**: 需要开源你的修改，商用需注意
- **BUSL**: 时间限制，看条款
- **自研**: 无风险但成本高

### 更新频率
- 每月更新一次 stars/活跃度
- 新项目启动时强制更新相关能力区
