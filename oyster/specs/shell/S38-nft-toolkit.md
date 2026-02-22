---
task_id: S38-nft-toolkit
project: shell-vibe-ide
priority: 3
estimated_minutes: 45
depends_on: ["S21-contract-interaction"]
modifies: ["web-ui/app/components/nft/metadata-editor.tsx", "web-ui/app/components/nft/collection-manager.tsx", "web-ui/app/lib/nft/ipfs-upload.ts", "web-ui/app/lib/nft/nft-templates.ts", "templates/nft/"]
executor: glm
---

## 目标

创建 NFT 专业工具包：元数据编辑器、IPFS 上传、Collection 管理。

## 开源方案

- **Metaplex JS SDK**: NFT 标准 (Solana)
- **Pinata SDK**: github.com/PinataCloud/pinata (IPFS pinning)
- **NFT.storage**: github.com/nftstorage/nft.storage (免费 IPFS)
- **thirdweb SDK**: NFT 铸造和管理

## 步骤

1. NFT 元数据编辑器:
   - 可视化表单: name, description, image, attributes
   - JSON 预览
   - 图片上传 (拖拽)
   - Attributes 编辑 (trait_type + value)
2. IPFS 上传:
   - 集成 Pinata 或 NFT.storage
   - 上传图片 → 获取 IPFS hash
   - 上传元数据 JSON → 获取 metadata URI
3. Collection 管理面板:
   - 创建 Collection (name, symbol, royalty)
   - 批量铸造
   - 查看已铸造 NFT 列表
4. NFT 模板 (新增):
   - PFP Collection (SVM + EVM)
   - Dynamic NFT (SVG on-chain)
   - Soul-bound Token (SBT)
   - Music NFT
5. NFT 预览:
   - 在 IDE 内渲染 NFT 图片
   - 模拟 OpenSea/Magic Eden 展示效果

## 验收标准

- [ ] 元数据编辑器工作
- [ ] IPFS 上传并获取 hash
- [ ] Collection 创建流程
- [ ] 批量铸造
- [ ] NFT 预览

## 不要做

- 不要实现 NFT 交易/市场
- 不要存储用户的 NFT 资产
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
