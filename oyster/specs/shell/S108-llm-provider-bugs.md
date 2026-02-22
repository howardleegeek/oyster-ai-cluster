---
task_id: S108-llm-provider-bugs
project: shell
priority: 1
estimated_minutes: 15
depends_on: []
modifies: ["web-ui/app/lib/modules/llm/providers/minimax.ts"]
executor: glm
---
## 目标
修复 LLM Provider 3 个 bug (#25-#27)

## Bug 清单

25. AbortController 泄露 — catch 区分 AbortError vs 网络错误，分别处理
26. maxTokenAllowed 硬编码 8000 — 从模型配置动态读取
27. `(await response.json()) as any` — 定义 MinimaxResponse interface，加 schema 校验

## 验收标准
- [ ] AbortError 和网络错误有不同处理
- [ ] maxToken 不硬编码
- [ ] response 有类型定义
- [ ] TypeScript 编译通过

## 不要做
- 不加新 provider
- 不改 LLM 调用逻辑
