---
task_id: S62-opcodes-viewer
project: shell-vibe-ide
priority: 3
estimated_minutes: 20
depends_on: ["S05-build-integration"]
modifies: ["web-ui/app/components/workbench/OpcodesViewer.tsx"]
executor: glm
---

## 目标

字节码反汇编查看器：编译后查看 EVM opcodes 和 Solana BPF 指令，帮助开发者理解底层行为。

## 步骤

1. `web-ui/app/components/workbench/OpcodesViewer.tsx`:
   - EVM 反汇编:
     - 读取编译产物的 bytecode hex
     - 逐字节解析 opcode (PUSH1, MSTORE, CALL, SSTORE 等)
     - 参考 https://www.evm.codes 的 opcode 表 (硬编码 ~150 个 opcode)
     - 显示: offset | hex | opcode | operand
     - 语法高亮: PUSH 类蓝色, STOP/REVERT 红色, CALL 类黄色
   - Gas 标注: 在每个 opcode 旁显示基础 gas cost
   - 搜索/过滤: 按 opcode 名称筛选
   - 点击 opcode → 显示简要说明
2. SVM 暂不实现 (BPF 反汇编太复杂)

## 验收标准

- [ ] EVM bytecode 正确反汇编
- [ ] opcode 高亮和 gas 标注
- [ ] 搜索过滤可用
- [ ] opcode 说明弹出

## 不要做

- 不要实现 SVM BPF 反汇编
- 不要实现 source mapping (太复杂)
- 不要引入外部反汇编库 (硬编码 opcode 表够用)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
