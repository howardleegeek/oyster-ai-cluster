# SOP: Oyster Discord 客服 (Oysterguard)

目标: 在 `#general-english` / `#general-chinese` 里用 **Reply 逐条**、**慢速**、**短回复** 解决用户问题; 误发内容只删自己发的, 绝不删用户消息。

## 0) 运行前检查
- 关闭占用同一 profile 的 Chromium: `pkill -f \"discord-admin/user-data\" || true`
- 确保已登录 Discord (脚本默认使用 `./user-data` 持久化 profile)

## 1) 快速冒烟 (不发消息)
```bash
cd ~/Downloads/discord-admin
node discord_smoke_test.mjs --headless --iterations 1
```
验收:
- 能看到频道消息 (不是 `no messages visible`)
- 右键/更多菜单里能看到 `回复` (Reply)

## 2) 清理误发 (只删我们自己的 dump)
```bash
cd ~/Downloads/discord-admin
# 清理 “rThanks ...” 这类前缀错发
node discord_purge_bad_r_prefix.mjs --channel 1404870331759591575
# 清理模板 dump (按 permalink 列表或自动扫描)
node discord_purge_templates.mjs --channel 1404870331759591575```
验收:
- 跑完后用状态快照确认: `node discord_capture_state.mjs --channel 1404870331759591575 --all --headless`

## 3) 审计用户抱怨点 (生成待回复清单)
```bash
cd ~/Downloads/discord-admin
node discord_disappointment_audit.mjs https://discord.com/channels/1404726112159793172/1404870331759591575 --limit 80
```
产物:
- `audit/<timestamp>/report.md` (人工快速扫一眼)
- `audit/<timestamp>/messages_*.json` (原始抓取)

要求:
- 后续发送必须是 **逐条 Reply** (不是一条里 @多个人)
- 单条 1-2 句, 不要“模板腔”, 不要长段落

## 4) 回复执行 (逐条, 8-15s 间隔)
```bash
cd ~/Downloads/discord-admin
node discord_reply_1by1.mjs audit/<timestamp>/report.json --delay-ms 12000```
验收:
- 每条回复都出现在正确的引用位置 (UI 有 Reply 关联)
- 不出现连续刷屏式长模板

## 5) 单点 debug (某条消息 Reply 打不开)
```bash
cd ~/Downloads/discord-admin
node discord_reply_open_debug.mjs --message <messageId> --channel 1404870331759591575
```
产物:
- `output/reply-open-...png` 一组步骤截图 (goto/hover/more/menu/reply/composer)

