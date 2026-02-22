# Codex Browser Agent MCP — 最强浏览器 Infra

> Opus 写 spec, Codex 执行
> 优先级: P0 (解锁 Codex 浏览器能力 = Opus token 节省 15-20%)

## 目标

给 Codex 一个 MCP server，让它能像 Claude in Chrome 一样操作浏览器：
截图 → GPT-5.3 看图理解 → 决定操作 → 执行 → 再截图验证

## 架构

```
Codex CLI
  ↓ MCP protocol (stdio)
Browser Agent MCP Server (Node.js)
  ├── CDP Client (ws://localhost:9222)
  │   ├── Page.captureScreenshot → base64 png
  │   ├── DOM.getDocument → accessibility tree
  │   ├── Input.dispatchMouseEvent → click
  │   ├── Input.dispatchKeyEvent → type
  │   └── Page.navigate → goto url
  ├── Screenshot → 自动转为 base64 返回给 Codex (GPT-5.3 多模态)
  └── Smart Element Finder (类似 Claude in Chrome 的 find)
```

## MCP Tools (暴露给 Codex 的)

### 1. `browser_screenshot`
- 参数: `{ tabIndex?: number, selector?: string }`
- 返回: base64 PNG 图片 (Codex GPT-5.3 可直接看)
- 可选: 只截某个元素区域

### 2. `browser_navigate`
- 参数: `{ url: string }`
- 返回: `{ title, url, status }`

### 3. `browser_click`
- 参数: `{ x: number, y: number }` 或 `{ selector: string }` 或 `{ text: string }`
- text 模式: 自动在 DOM 中找包含该文字的可点击元素
- 返回: `{ success, screenshot_base64 }` (点击后自动截图)

### 4. `browser_type`
- 参数: `{ text: string, selector?: string }`
- 如果有 selector → 先点击该元素再输入
- 返回: `{ success, screenshot_base64 }`

### 5. `browser_read_page`
- 参数: `{ mode: "accessibility" | "text" | "interactive" }`
- accessibility: 返回类似 Claude in Chrome 的 accessibility tree
- text: 返回页面纯文本 (用 Readability 提取)
- interactive: 只返回可交互元素 (按钮/链接/输入框)
- 返回: 文本内容 (省 token，不用截图)

### 6. `browser_find`
- 参数: `{ query: string }` (自然语言: "login button", "search bar")
- 实现: 遍历 DOM，用 aria-label/innerText/role 匹配
- 返回: `[{ ref, tag, text, rect: {x,y,w,h} }]`

### 7. `browser_scroll`
- 参数: `{ direction: "up"|"down", amount?: number }`
- 返回: `{ screenshot_base64 }`

### 8. `browser_wait`
- 参数: `{ seconds?: number, selector?: string }`
- selector 模式: 等元素出现 (最多 10s)
- 返回: `{ success }`

### 9. `browser_tabs`
- 参数: `{}`
- 返回: `[{ id, title, url }]` — 列出所有 Chrome tabs

### 10. `browser_execute_js`
- 参数: `{ code: string }`
- 返回: `{ result }`

## 关键设计决策

### 截图自动返回
- `browser_click` 和 `browser_type` 操作后**自动附带截图**
- 这样 Codex 不需要额外调一次 screenshot，省一轮交互
- 截图压缩: JPEG quality 60, 最大 1280x720 (够看清，省 token)

### Token 优化
- 默认用 `browser_read_page` (文本) 而不是截图
- 截图只在需要视觉判断时使用
- accessibility tree 比截图便宜 10 倍

### 多 CDP 端口支持
- 默认连 localhost:9222
- 可配置连 9223 (Puffy 号) 或其他端口
- 通过 MCP config 的 env 传入: `CDP_PORT=9222`

### 错误处理
- CDP 连接断开 → 自动重连 (3 次)
- 元素找不到 → 返回 DOM 快照帮助 Codex 调试
- 超时 → 返回最后一张截图 + 错误信息

## 文件结构

```
~/Downloads/codex-browser-mcp/
├── package.json
├── src/
│   ├── index.ts          # MCP server 入口
│   ├── cdp-client.ts     # Chrome DevTools Protocol 封装
│   ├── tools/
│   │   ├── screenshot.ts
│   │   ├── navigate.ts
│   │   ├── click.ts
│   │   ├── type.ts
│   │   ├── read-page.ts
│   │   ├── find.ts
│   │   ├── scroll.ts
│   │   ├── wait.ts
│   │   ├── tabs.ts
│   │   └── execute-js.ts
│   └── utils/
│       ├── dom-parser.ts     # accessibility tree 构建
│       ├── element-finder.ts # 自然语言 → DOM 元素匹配
│       └── image-utils.ts    # 截图压缩/裁剪
├── tsconfig.json
└── README.md
```

## Codex config.toml 集成

```toml
[mcp.browser-agent]
type = "command"
command = ["node", "/Users/howardlee/Downloads/codex-browser-mcp/dist/index.js"]

[mcp.browser-agent.env]
CDP_HOST = "localhost"
CDP_PORT = "9222"
```

Mac-2 配置 (两个 Chrome 实例):
```toml
[mcp.browser-twitter]
type = "command"
command = ["node", "/Users/howardlee/Downloads/codex-browser-mcp/dist/index.js"]
[mcp.browser-twitter.env]
CDP_PORT = "9222"

[mcp.browser-puffy]
type = "command"
command = ["node", "/Users/howardlee/Downloads/codex-browser-mcp/dist/index.js"]
[mcp.browser-puffy.env]
CDP_PORT = "9223"
```

## 验收标准

- [ ] Codex 能通过 MCP 截图并"看到"页面内容
- [ ] Codex 能用自然语言找到页面元素 (browser_find)
- [ ] Codex 能完成一个完整流程: 打开 Twitter → 找到发推按钮 → 输入内容
- [ ] click/type 操作后自动返回截图
- [ ] 在 Mac-2 上连接 CDP 9222/9223 都正常
- [ ] 错误处理: CDP 断连自动重连

## 实现顺序

1. **Phase 1**: CDP client + screenshot + navigate + read_page (最小可用)
2. **Phase 2**: click + type + find + scroll (交互能力)
3. **Phase 3**: execute_js + tabs + wait + 错误处理 (完整)

## 依赖

- `ws` — WebSocket (CDP 通信)
- `@anthropic-ai/sdk` 或 `@modelcontextprotocol/sdk` — MCP server
- `linkedom` 或 `cheerio` — DOM 解析 (用于 accessibility tree)
- `sharp` — 图片压缩 (可选，也可用 Canvas)

## 估计工时

- Codex 实现: 2-4 小时 (3 个 phase)
- Opus review: 15 分钟
- 集成测试: 30 分钟
