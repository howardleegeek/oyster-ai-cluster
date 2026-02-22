---
task_id: S104-solidity-test-bugs
project: shell
priority: 0
estimated_minutes: 20
depends_on: []
modifies: ["demo/evm-vault/src/SimpleVault.sol", "demo/evm-vault/test/SimpleVault.t.sol", "tests/", "templates/registry.json"]
executor: glm
---
## 目标
修复 Solidity + 测试的 10 个 bug (#20-#21, #28-#31, #37-#39, #47)

## Bug 清单

### Critical
20. **SimpleVault 无 withdraw** — 资金永久锁定。修复: 加 withdraw() 函数 + ReentrancyGuard
21. **expectRevert message 错误** — 期望 "Wrong message" 实际 "Must send ETH"。修复: 改成正确 message
47. **无 reentrancy guard** — withdraw 需要 guard。修复: 继承 OpenZeppelin ReentrancyGuard

### High
28. **mcpConfig.test.ts 结构不匹配** — 期望 config.mcpServers 实际是扁平。修复: 改测试匹配实际 JSON 结构
29. **capabilities 期望不匹配** — 修复: 改成实际 capabilities
30. **fuzz.test.js reports 写错目录** — 修复: 用 __dirname 相对路径
31. **init.sh 删除 tests/** — 修复: 改 init.sh 不删 tests/
37. **schema 缺 additionalProperties: false** — 修复: 加上
38. **registry sourceURL 指向不存在仓库** — 修复: 改成相对路径或注释标注 placeholder
39. **registry 格式不一致** — 修复: 统一 JSON 格式

## 验收标准
- [ ] SimpleVault 有 withdraw() + ReentrancyGuard
- [ ] `forge test` 在 demo/evm-vault/ 全部通过
- [ ] mcpConfig.test.ts 的期望与实际 JSON 一致
- [ ] init.sh 不删除 tests/ 和 .opencode/

## 不要做
- 不改合约业务逻辑（只修 bug）
- 不加新测试文件
- 不动 web-ui
