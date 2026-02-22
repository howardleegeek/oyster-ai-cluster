## 任务: 研究 Z.AI 完整能力矩阵，产出接入优先级报告

### 背景
Z.AI (智谱) 提供大量 GLM 模型和 MCP 能力，大部分已接入但未充分利用。
需要系统性评估所有可用能力，确定哪些值得接入，哪些对当前项目有价值。

### 已知能力清单 (需要验证 + 补充)

**已接入:**
- GLM-5 (代码执行，via z.ai Anthropic API)
- GLM-4.6V Vision MCP (@z_ai/mcp-server, 8 个视觉工具)
- Web Search MCP (远程 HTTP)
- Web Reader MCP (远程 HTTP)
- Zread MCP (GitHub 仓库探索)

**待评估:**
- AutoGLM-Phone (手机自动化, ADB 控制, 9B 端侧, 限时免费) — ClawPhones 测试价值
- GLM-OCR (文档/PDF/手写, 0.9B, $0.03/1M tok)
- CogView-4 (文生图, $0.01/张)
- GLM-ASR-2512 (语音转文字, $0.03/1M tok)
- GLM-Image (高级文生图, $0.015/张)
- Function Calling (GLM-5/GLM-4.6)
- Context Caching (80% off)
- 免费模型: GLM-4.7-Flash, GLM-4.5-Flash, GLM-4.6V-Flash

### 研究任务 (可并发)

**Task 1: AutoGLM-Phone 深度调研**
- API 文档、调用方式、ADB 集成方法
- 9B 端侧部署 vs API 调用
- 支持的 app 列表和操作类型
- ClawPhones 测试自动化可行性评估
- 限时免费的期限和后续定价

**Task 2: Z.AI MCP Server 完整工具清单**
- @z_ai/mcp-server 的所有 8 个视觉工具详细文档
- 每个工具的输入输出格式
- 与 Claude Code 集成的最佳实践
- Web Search/Reader/Zread 的完整 API spec

**Task 3: 免费模型能力测试**
- GLM-4.7-Flash vs GLM-4.5-Flash 对比
- 能否替代 Haiku 做轻量搜索/分析任务
- 通过 z.ai Anthropic API 调用免费模型的方法
- 用 OpenClaw 接入免费模型的可行性

**Task 4: Context Caching + Function Calling 评估**
- Context Caching 的 API 用法和限制
- 对我们的 GLM 执行池的 token 节省量化
- Function Calling 在 Agent Swarm 中的应用

### 产出
- `specs/glm-capability-matrix.md` — 完整能力矩阵 + 接入优先级
- 每个能力标注: 价格、对哪个项目有价值、接入难度、建议优先级 (P0/P1/P2)

### 验收标准
- [ ] 所有已知能力都有评估
- [ ] AutoGLM-Phone 有可行性结论
- [ ] 免费模型有实际测试结果
- [ ] 产出 prioritized 接入计划
