## 目标
修复合并后的 JSON 配置错误，让项目能 build

## 约束
- 只改配置文件，不动业务代码
- TypeScript + Vite + Remix 技术栈

## 具体修复
1. `web-ui/tsconfig.json` — 删除第 27 行 JSON 注释 (`// vite takes care...`)
2. `web-ui/package.json` — 合并两个重复的 "scripts" 对象为一个，保留所有 script
3. `deploy.config.sample.json` — 删除所有 JSON 注释，改用 "_comment" 字段
4. `mcp-server/package.json` — 确保 `@modelcontextprotocol/sdk` 在 dependencies 里

## 验收标准
- [ ] `cd web-ui && npx tsc --noEmit` 不报 tsconfig 解析错误
- [ ] `cd mcp-server && npx tsc --noEmit` 不报缺依赖
- [ ] 所有 .json 文件通过 `python3 -c "import json; json.load(open('file'))"`

## 不要做
- 不改业务逻辑
- 不加新功能
- 不改 UI