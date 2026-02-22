---
task_id: S101-runner-critical-bugs
project: shell
priority: 0
estimated_minutes: 30
depends_on: []
modifies: ["runner/src/index.js", "runner/src/fuzz.js", "runner/package.json"]
executor: glm
---
## 目标
修复 runner 的 11 个 Critical/High bug (#1-#7, #32-#35)

## Bug 清单

### Critical
1. **ESM+CJS 冲突** — fuzz.js 用 require() 但 package.json 声明 "type": "module"。修复: 把 fuzz.js 改成 ESM (import)
2. **resolve 命名冲突** — L96 Promise resolve 和 L32 path.resolve 同名。修复: 把 import { resolve } from 'path' 改成 import { resolve as pathResolve }
3. **Anvil 进程不清理** — spawn('anvil', { detached: true }) 后无 unref 无 cleanup。修复: 加 process.on('exit') 清理 + anvil.unref()
4. **network 变量混乱** — anvil 时 network='local' 但 options.network 仍是 'anvil'。修复: 统一用一个变量
5. **forge create 命令拼接错误** — 整个命令作为可执行文件名。修复: 拆分成 command + args 数组
6. **options.network 和 network 混用** — 同 #4，统一变量
7. **Deploy 没传 private key** — forge create 缺少 --private-key。修复: 加 --private-key 参数（从 env 读）

### High
32. **Slither INFO 被当 issue** — 过滤掉 INFO: 级别日志
33. **actionReport 无 try/catch** — JSON.parse 加 try/catch
34. **parseArgs 不支持 --key=value** — 加 split('=') 处理
35. **Test 解析只支持 Forge 格式** — 加 Hardhat 输出匹配

## 验收标准
- [ ] `node runner/src/index.js --help` 不报 ESM 错误
- [ ] fuzz.js 用 ESM import
- [ ] deploy 命令正确拆分 command/args
- [ ] Anvil 进程在脚本退出时被清理

## 不要做
- 不改 runner 功能逻辑
- 不加新功能
- 不动 web-ui
