---
task_id: S98-chat-ux-polish
project: shell
priority: 1
estimated_minutes: 30
depends_on: [S94-build-fix-critical]
modifies: ["web-ui/app/components/chat/"]
executor: glm
---
## 目标
提升 chat 体验到 Noah 水平：流畅、有上下文、有项目感知

## 约束
- 基于现有 ai-chat.tsx / Chat.client.tsx 扩展
- 不换 AI 后端，只改前端交互
- React + TypeScript

## 实现
1. 项目上下文面板：chat 侧边栏显示当前项目文件树 + 合约状态
2. 智能建议：根据当前代码自动显示 "部署到测试网" / "运行测试" / "优化 Gas" 快捷按钮
3. 流式输出优化：代码块实时高亮 + 可折叠
4. 历史记录：conversation 持久化到 localStorage，重开浏览器能恢复
5. 操作反馈：合约编译/测试/部署的结果直接嵌入 chat 流

## 验收标准
- [ ] 项目上下文面板在 chat 旁边可见
- [ ] 至少 3 个智能建议按钮
- [ ] 代码块有语法高亮
- [ ] localStorage 保存/恢复 conversation
- [ ] TypeScript 编译通过

## 不要做
- 不改 AI 模型调用逻辑
- 不动后端 API
- 不加新依赖 >3 个
