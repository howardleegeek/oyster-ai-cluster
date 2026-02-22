---
executor: glm
task_id: S99-aesthetic-detector-setup
project: dispatch
priority: 1
depends_on: []
modifies:
  - scripts/install-mcp-tools.sh
  - nodes.json
---
executor: glm

## 目标

将「审美检测器」(Aesthetic Detector) MCP 工具集成到 Codex 集群，让所有执行节点都能使用前端审美评审能力。

## 约束
- 不修改 dispatch.py 核心逻辑
- 不改动 task-wrapper.sh 的基础架构
- MCP 配置通过共享配置或远程安装方式分发

## 具体改动

### 1. 更新安装脚本 (scripts/install-mcp-tools.sh)
- 添加 `--cluster` 选项，支持远程节点安装
- 支持代码节点: codex-node-1, glm-node-2/3/4
- 支持 OCI 节点: oci-paid-1, oci-paid-3, oci-arm-1
- 支持 mac2

### 2. 创建节点 MCP 配置模板
在 `~/.mcp-servers/` 目录结构共享:
```
~/.mcp-servers/
├── install-cluster.sh      # 集群批量安装脚本
├── opencode.json          # MCP 配置模板
└── design-critique-mcp/   # 编译后的工具
```

### 3. 修改 nodes.json (可选)
添加节点 MCP 能力标记:
```json
{
  "name": "codex-node-1",
  "mcp_enabled": true,
  "mcp_tools": ["playwright", "lighthouse", "design-critique"]
}
```

### 4. 验证方案
在 codex-node-1 上测试:
- SSH 到节点执行 `npx @playwright/mcp@latest --version`
- 验证 lighthouse-mcp-server 可用

## 验收标准
- [ ] 安装脚本支持 `--cluster` 参数
- [ ] 至少在一个远程节点上验证 MCP 工具可用
- [ ] 更新 skill 文档说明分布式使用方式
