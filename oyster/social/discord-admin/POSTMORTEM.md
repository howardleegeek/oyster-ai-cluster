# Discord Web + Playwright 操作问题复盘（工程团队可直接复制）

会话/产物锚点：
- Codex thread: `019c3ac8-b1df-7d23-886a-366df44de837`
- 审计报告：`/Users/howardli/Downloads/discord-admin/audit/20260207-173934-disappointment/report.md`
- 相关脚本目录：`/Users/howardli/Downloads/discord-admin/`

## 1. Playwright 扩展模式不稳定
- `playwright-mcp --extension` 多次出现 `Extension disconnected`，无法接管已登录 Chrome，会导致自动化直接不可用。
- 只能退回到本地 Playwright 启动独立 Chromium + `launchPersistentContext(user-data)`。

## 2. Playwright Node API 缺少 a11y 接口
- Node 版 Playwright 里 `page.accessibility` 为 `undefined`，导致基于 `accessibility.snapshot()` 的抓取方案不可用。
- 必须改为纯 DOM/ARIA 选择器抓取。

## 3. Discord Web：headless vs non-headless 行为不一致
- 同一份 `user-data` 下，headless 模式偶发：页面已进入 `/channels/<guild>/<channel>`，但频道列表选择器 `[data-list-item-id^="channels___"]` 返回 0。
- non-headless 下同样代码能稳定拿到频道列表（约 20+ 项）。需要显式等待、重试、或强制 non-headless。

## 4. 频道/消息 DOM 结构高度不稳定（class hash 频繁变化）
- 依赖 className（如 `messageListItem__...`）不可靠，只能依赖 ARIA 和结构性属性：
  - 频道：`[data-list-item-id^="channels___"]` + `aria-label`
  - 消息：`li[id^="chat-messages-<channel>-<message>"]` + `[id^="message-content-"]`
- 作者名提取也会被时间戳/格式污染，需要多 selector fallback + 清洗。

## 5. 消息列表是虚拟滚动（virtualized）
- DOM 中只保留可视范围消息，抓历史必须对消息 scroller 做多次向上滚动触发加载，否则会严重漏数据。
- 需要找到真正可滚动容器（`overflowY: scroll/auto` 且 `scrollHeight > clientHeight`），并做节流与“无新消息退出”的终止条件。

## 6. 分类/语言识别容易误伤公告内容
- 欢迎帖/公告含 “claim/passport/Founder Pass” 等关键词，若直接关键词匹配会把教程当成抱怨。
- 需要过滤：
  - 跳过公告作者/系统作者（如服务器官方账号）
  - 跳过明显“指令型/教程型”文本（包含链接 + “claim your …”等模式）
- 语言识别不能只靠“包含中文就判 zh”，应按脚本占比做 dominant-language。

## 7. 自动发消息容易造成刷屏/挤在一起
- “一个消息里 @ 多人”的批量回复会被用户感知为 spam，阅读体验差。
- 正确形态应是：打开某条原消息 -> 点击 `Reply`（threaded reply）-> 发 1 条；并限速（例如 1 条/8-15 秒）+ 记录已回复避免重复。

## 8. 删除历史错误消息不可靠
- 删除依赖 hover/右键/菜单/二次确认；菜单项在中英文不同（Delete/删除消息），且元素经常不在可视 DOM，需要滚动回去。
- 需要“滚动扫描 -> 识别候选 -> 删除 -> 再扫描”的循环，且要防误删（必须校验作者为己方账号 + 文本特征命中）。

## 9. 右键目标不同会弹出不同菜单（导致“删不掉/看起来没动作”）
- 同一条消息在不同 DOM 区域右键，弹出的菜单内容不一样：
  - 多数消息：右键 `message-content` 能看到完整菜单（含“删除信息/删除消息/Delete Message”）。
  - 少数消息：右键 `message-content` 可能被 `layerContainer/clickTrap` 拦截，只弹极简菜单（例如只剩“复制链接”），导致自动化拿不到删除入口。
- 可复现样例：
  - Guild: `1404726112159793172`，Channel: `1404870331759591575`（`#general-english`）
  - Message liId：`chat-messages-1404870331759591575-1469871129568215214`
  - 删除失败常见报错：`... subtree intercepts pointer events`（`layerContainer__.../clickTrapContainer__...`）
- 解决办法（已验证有效）：改为对同一条消息里的 `time` 元素右键，再点击“删除信息/删除消息/Delete Message”，稳定可删除。
- 工程建议：封装 `openMessageContextMenu()`：优先右键 `time`，fallback 右键 `message-content`，再 fallback 右键 `li`；每次操作前先 `Escape` 清理残留菜单/遮罩；菜单定位用 `role=menuitem` + 中英文兼容。

## 脚本映射（当前仓库内已有）
- 抓取近期消息：`/Users/howardli/Downloads/discord-admin/discord_scrape_recent.mjs`
- 失望点审计 + 草拟回复：`/Users/howardli/Downloads/discord-admin/discord_disappointment_audit.mjs`
- 逐条 Reply（1 人 1 条）：`/Users/howardli/Downloads/discord-admin/discord_reply_1by1.mjs`
- 删除之前“挤在一起”的 dump：`/Users/howardli/Downloads/discord-admin/discord_delete_our_dump.mjs`
