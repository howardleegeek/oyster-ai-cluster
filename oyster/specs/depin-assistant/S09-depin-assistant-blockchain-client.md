---
task_id: S09-depin-assistant-blockchain-client
project: depin-assistant
priority: 2
depends_on: []
modifies: ["src/services/blockchainClient.js"]
executor: glm
---
## 目标
实现区块链交互模块，封装Ethers.js基本操作

## 技术方案
- 封装wallet连接和签名
- 提供查询余额和发送交易接口
- 错误处理和重试机制

## 约束
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 可连接钱包并查询余额
- [ ] 支持交易发送
- [ ] test 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
