---
task_id: S57-calldata-codec
project: shell-vibe-ide
priority: 3
estimated_minutes: 20
depends_on: ["S40-abi-manager"]
modifies: ["web-ui/app/components/workbench/CalldataCodec.tsx"]
executor: glm
---

## 目标

Calldata 编解码器：粘贴 calldata hex → 解码出函数名+参数，或选择函数+填参数 → 编码成 calldata。

## 步骤

1. `web-ui/app/components/workbench/CalldataCodec.tsx`:
   - Tab 1 — Decode:
     - 输入: 粘贴 0x calldata hex string
     - 如果已有 ABI (从 S40 ABI manager): 自动匹配 function selector → 显示函数名 + 解码参数
     - 如果无 ABI: 显示 raw selector (4 bytes) + raw params (32-byte chunks)
     - 用 ethers.Interface.decodeFunctionData()
   - Tab 2 — Encode:
     - 选择合约 → 选择函数 → 填入参数值
     - 实时生成 calldata hex
     - 用 ethers.Interface.encodeFunctionData()
   - 额外功能:
     - 4byte.directory 查询未知 selector
     - 复制按钮
2. 使用 ethers.js v6 的 Interface 类做编解码

## 验收标准

- [ ] Decode: 粘贴 calldata 能正确解码
- [ ] Encode: 选函数填参数能正确编码
- [ ] 4byte selector 查询可用
- [ ] 支持复杂类型 (tuple, array, bytes)

## 不要做

- 不要实现 SVM 版 (Borsh 序列化太不同了)
- 不要实现批量解码
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
