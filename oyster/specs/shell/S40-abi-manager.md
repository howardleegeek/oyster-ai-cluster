---
task_id: S40-abi-manager
project: shell-vibe-ide
priority: 2
estimated_minutes: 35
depends_on: ["S21-contract-interaction"]
modifies: ["web-ui/app/**/*.tsx", "web-ui/package.json"]
executor: glm
---

## 目标

创建 ABI/IDL 管理器：导入、查看、对比任意合约的接口。

## 开源方案

- **WhatsABI**: github.com/shazow/whatsabi (1.1k stars, MIT) — 从字节码推断 ABI
- **Sourcify API**: 获取已验证合约 ABI
- **Anchor IDL**: Anchor 程序的接口描述

## 步骤

1. ABI 导入:
   - 从合约地址推断 (WhatsABI)
   - 从 Etherscan/Sourcify 获取 (已验证合约)
   - 手动粘贴 ABI JSON
   - 从编译输出自动提取
2. ABI 查看器:
   - 按类型分组: Functions / Events / Errors
   - 每个函数: name, inputs, outputs, stateMutability
   - 可折叠/展开
3. ABI 对比:
   - 选择两个版本的 ABI
   - 高亮差异 (新增函数, 修改参数, 删除函数)
   - 向后兼容性检查
4. IDL 管理 (Solana):
   - 从 Anchor 项目自动生成 IDL
   - IDL 查看器 (instructions, accounts, types)
5. ABI 导出:
   - JSON 文件
   - TypeScript 类型定义
   - ethers.js/viem interface

## 验收标准

- [ ] WhatsABI 推断工作
- [ ] ABI 查看器显示函数/事件
- [ ] 从合约地址获取 ABI
- [ ] ABI 对比功能
- [ ] 导出 TypeScript 类型

## 不要做

- 不要自己实现 ABI 推断 (用 WhatsABI)
- 不要实现 ABI encode/decode (用 viem)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
