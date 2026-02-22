# Test Plan: Discord-admin 工具链回归

目的: 每次工程修复后, 用最小成本验证 “能看到消息 -> 能打开 Reply UI -> 不会误删 -> 不会挤在一起”。

## 1) Profile 锁检查
```bash
ps aux | rg -i \"Chrome|Chromium|playwright\" | rg \"discord-admin/user-data\" || true
```
验收:
- 没有残留进程占用 `~/Downloads/discord-admin/user-data`

## 2) 冒烟: 能看到消息 + 菜单里有“回复”
```bash
cd ~/Downloads/discord-admin
node discord_smoke_test.mjs --headed --iterations 1
```
验收:
- 输出里 `replyUi: true`
- 不出现 `error: \"no messages visible\"`

## 3) 单条 Reply 打开可用性 (不发消息)
挑一个 messageId (例如失败过的):
- `1451424861426679885` (Mykhail)
- `1456200335591870574` (venson)
```bash
cd ~/Downloads/discord-admin
node discord_reply_open_debug.mjs --message 1451424861426679885
```
验收:
- `output/reply-open-...-final-*.png` 中 composer 可见
- 终端 JSON 里 `composer-visible: true`

## 4) 清理脚本安全性 (只删我们自己的错发)
```bash
cd ~/Downloads/discord-admin
node discord_purge_bad_r_prefix.mjs --channel 1404870331759591575 --headed
```
验收:
- 只删除 `Oysterguard` 自己的错发, 不影响用户消息

## 5) 状态快照 (用于人工复核)
```bash
cd ~/Downloads/discord-admin
node discord_capture_state.mjs --channel 1404870331759591575 --all --headed
```
验收:
- `output/discord-state-*.png` 能看到频道正在正常滚动, 没有残留模板 dump

