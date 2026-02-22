---
task_id: S56-ipfs-deploy
project: shell-vibe-ide
priority: 2
estimated_minutes: 25
depends_on: ["S10-deploy"]
modifies: ["web-ui/app/components/workbench/IpfsPanel.tsx", "web-ui/app/lib/stores/ipfs.ts"]
executor: glm
---

## 目标

IPFS/Arweave 去中心化部署：上传合约元数据、前端静态文件到 IPFS (Pinata) 或 Arweave (Bundlr)。

## 步骤

1. `web-ui/app/lib/stores/ipfs.ts`:
   - nanostores atom: `ipfsProvider` ("pinata" | "arweave")
   - `uploadStatus` (idle/uploading/done/error)
   - `uploadHistory`: [{cid, filename, size, timestamp, provider}]
2. `web-ui/app/components/workbench/IpfsPanel.tsx`:
   - 上传目标选择: Pinata IPFS / Arweave
   - 文件选择: 从编辑器选文件 或 整个 build 目录
   - 上传进度条
   - 上传成功后显示:
     - IPFS CID + gateway 链接 (ipfs.io/ipfs/...)
     - Arweave TX ID + 链接
   - 历史记录列表
3. API 集成:
   - Pinata: `POST https://api.pinata.cloud/pinning/pinFileToIPFS`
   - Arweave/Bundlr: `POST https://node1.bundlr.network/tx`
   - API key 存在用户设置中 (不硬编码)

## 验收标准

- [ ] Pinata IPFS 上传可用
- [ ] 上传后 CID 可访问
- [ ] 历史记录持久化
- [ ] API key 配置界面

## 不要做

- 不要跑本地 IPFS 节点
- 不要自动 pin (用户手动触发)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
