---
task_id: S111-ainatspec-projectcmd-bugs
project: shell
priority: 1
estimated_minutes: 25
depends_on: []
modifies: ["web-ui/app/utils/aiNatSpec.ts", "web-ui/app/utils/projectCommands.ts", "web-ui/app/utils/constants.ts"]
executor: glm
---
## 目标
修复 AI NatSpec + projectCommands + constants 10 个 bug (#47-#56)

## Bug 清单

### aiNatSpec.ts
47. 函数名正则漏匹配 — `function\s+(\w+)\s*\(` 改为支持空格: `function\s+(\w+)\s+\(`
48. 跨行 return 不匹配 — 改为多行匹配模式
49. Rust 漏掉 pub struct — 正则加 `(?:pub\s+(?:\(crate\)\s+)?)?struct`
50. 非指令函数误判 — 检查 fn 是否在 `#[program]` mod 内

### projectCommands.ts
51. 包管理器硬编码 npm — 检测 bun.lockb/pnpm-lock.yaml/yarn.lock 决定用哪个
52. `--template default` 插队 — 只在已知支持的 CLI 加此 flag
53. `echo "y"` 盲目 stdin — 用 `--yes` flag 替代 echo pipe
54. `escapeBoltArtifactTags` 正则不准 — 改用非贪婪 + 精确边界匹配

### constants.ts
55. DEFAULT_MODEL 硬编码 — 从环境变量 `DEFAULT_MODEL` 读取，fallback 到当前值
56. `providerBaseUrlEnvKeys` 懒加载空 — 改为 getter 函数延迟计算

## 验收标准
- [ ] `pub struct` 被正确识别
- [ ] 包管理器自动检测
- [ ] DEFAULT_MODEL 可通过 env 覆盖
- [ ] TypeScript 编译通过

## 不要做
- 不改 AI 模型调用
- 不加新 provider
