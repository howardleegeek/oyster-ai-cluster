---
task_id: S115-mcp-naming-config
project: shell
priority: 2
estimated_minutes: 10
depends_on: []
modifies: ["web-ui/app/lib/stores/mcp.ts"]
executor: glm
---
## 目标
修复 MCP 命名含混 bug (#75)

## Bug 清单

75. `MCP_SETTINGS_KEY = 'mcp_settings'` 命名含混 — 重命名为 `MCP_CONFIG_KEY = 'mcp_config'`，并加迁移逻辑读旧 key

## 验收标准
- [ ] 新 key 名 `mcp_config`
- [ ] 向后兼容读取旧 `mcp_settings` key
- [ ] TypeScript 编译通过

## 不要做
- 不改 MCP 功能逻辑
