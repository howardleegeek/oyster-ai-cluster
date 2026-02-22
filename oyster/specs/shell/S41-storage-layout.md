---
task_id: S41-storage-layout
project: shell-vibe-ide
priority: 3
estimated_minutes: 35
depends_on: ["S19-evm-debugger"]
modifies: ["web-ui/app/components/storage/storage-layout.tsx", "web-ui/app/components/storage/slot-viewer.tsx", "web-ui/app/lib/storage/layout-parser.ts", "web-ui/app/lib/storage/packing-analyzer.ts"]
executor: glm
---

## 目标

EVM 合约存储布局可视化，帮助开发者理解和优化 storage。

## 开源方案

- **sol2uml**: github.com/nickvdyck/sol2uml — Solidity 存储布局可视化
- **forge inspect --storage-layout**: Foundry 内置

## 步骤

1. 获取 storage layout:
   - `forge inspect {Contract} storage-layout --json`
2. 可视化:
   - Slot 表格: slot number, name, type, offset, bytes
   - 颜色编码: 不同类型不同颜色
   - Packing 效率指示 (哪些 slot 有空隙)
3. 优化建议:
   - 检测 storage packing 机会
   - AI 建议重新排列变量顺序以节省 gas
4. Storage 对比:
   - 合约升级前后的 storage layout 对比
   - 检测 storage collision (代理模式)
5. 实时 storage 查看:
   - 连接到 Anvil/测试网
   - 读取指定 slot 的当前值
   - slot 值解码 (根据 layout)

## 验收标准

- [ ] Storage layout 表格显示
- [ ] Packing 效率指示
- [ ] 优化建议
- [ ] Storage 对比
- [ ] 实时 slot 值读取

## 不要做

- 不要自己解析 Solidity AST (用 forge inspect)
- 不要实现 Solana account layout (不同模型)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
