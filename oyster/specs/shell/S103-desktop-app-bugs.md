---
task_id: S103-desktop-app-bugs
project: shell
priority: 1
estimated_minutes: 30
depends_on: []
modifies: ["desktop/src/App.tsx", "desktop/src-tauri/tauri.conf.json", "desktop/tauri.conf.json", "desktop/src-tauri/src/commands.rs", "desktop/src/mcpManager.ts"]
executor: glm
---
## 目标
修复 Desktop App 的 8 个 bug (#12-#19)

## Bug 清单

### Critical
12. **iframe 硬编码 localhost:5173** — 生产环境空白。修复: 用 Tauri asset 协议加载，或根据 import.meta.env 切换 URL
13. **sandbox allow-scripts+allow-same-origin** — 等于无 sandbox。修复: 移除 sandbox 属性或调整策略
14. **两个 tauri.conf.json 冲突** — productName 不同。修复: 删除 desktop/tauri.conf.json，只保留 src-tauri/ 下的
15. **CSP 设为 null** — 无安全策略。修复: 设合理 CSP (default-src 'self'; script-src 'self' 'unsafe-inline')
16. **kill -9 强杀** — 不优雅。修复: 先 SIGTERM，3 秒后 SIGKILL
17. **get_server_status 不验证进程存活** — 修复: 加 kill -0 pid 检查
18. **mcpManager __dirname bundle 后不对** — 修复: 用 import.meta.url 或 app.getPath()
19. **kill() 不等进程退出** — 修复: 等 'exit' event 后再 delete

## 验收标准
- [ ] 只剩一个 tauri.conf.json
- [ ] CSP 不是 null
- [ ] App.tsx 不硬编码 localhost
- [ ] TypeScript 编译通过

## 不要做
- 不改 UI 样式
- 不加新功能
- 不动 web-ui
