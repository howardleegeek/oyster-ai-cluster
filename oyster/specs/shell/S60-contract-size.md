---
task_id: S60-contract-size
project: shell-vibe-ide
priority: 3
estimated_minutes: 15
depends_on: ["S05-build-integration"]
modifies: ["web-ui/app/components/workbench/ContractSizeBar.tsx"]
executor: glm
---

## 目标

合约大小分析器：编译后显示字节码大小，对比 EVM 24KB 限制 和 Solana 10MB BPF 限制。

## 步骤

1. `web-ui/app/components/workbench/ContractSizeBar.tsx`:
   - 在 Build 完成后的报告中添加 size bar
   - EVM: 读取编译产物 JSON 的 `deployedBytecode` 字段 → 计算 hex 长度 / 2
     - 绿色: <20KB, 黄色: 20-24KB, 红色: >24KB
     - 显示: "12.5KB / 24KB (52%)"
   - SVM: 读取 .so 文件大小
     - 绿色: <5MB, 黄色: 5-10MB, 红色: >10MB
   - 多合约时列出每个合约的大小
   - 超限时显示优化建议提示 (使用 library, 拆分合约等)
2. 集成到 S17 Reports Dashboard 的 build report 中

## 验收标准

- [ ] EVM 合约显示字节码大小
- [ ] SVM 程序显示 .so 大小
- [ ] 颜色阈值正确
- [ ] 超限显示警告

## 不要做

- 不要实现自动优化
- 不要修改编译流程
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
