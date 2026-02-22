## 任务: Mac-2 错误反馈机制 + 账户管理体系

### 背景
Mac-2 (192.168.4.63) 已经跑起来了 (Chrome CDP 9222/9223 + launchd)。
现在需要:
1. 让 Mac-2 开始干活 — 验证 Twitter 登录态、跑第一个真实任务
2. 建立自动错误反馈机制 — Mac-2 出问题时自动检测、上报、修复
3. 建立统一账户管理体系 — 所有 key/credential 集中管理

Mac-2 SSH: `ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63`
Mac-1 隧道已通: localhost:9222 → Mac-2:9222, localhost:9223 → Mac-2:9223

---

## Part 1: 让 Mac-2 跑第一个真实任务

### 1a: 验证 Twitter 登录态
通过 Mac-1 隧道检查 Mac-2 Chrome 上的 Twitter 登录状态:
```bash
# 在 Mac-1 上 (通过隧道连 Mac-2 Chrome)
cd ~/Downloads/twitter-poster
python3 twitter_poster.py status --cdp-endpoint http://127.0.0.1:9222
# 或直接用 CDP 检查当前页面
curl -s http://127.0.0.1:9222/json | python3 -m json.tool
```

如果没有登录:
- 方案A: 从 Mac-1 rsync Chrome profile → Mac-2 (需先停 Mac-2 Chrome)
  ```bash
  # Mac-2 上先停 Chrome
  ssh mac2-cdp "launchctl unload ~/Library/LaunchAgents/ai.oyster.chrome-cdp-9222.plist"
  # rsync
  rsync -avz "/Users/howardli/Library/Application Support/Google/Chrome-CodexCDP/" howardlee@192.168.4.63:/Users/howardlee/chrome-cdp-9222/
  # Mac-2 重新启动 Chrome
  ssh mac2-cdp "launchctl load ~/Library/LaunchAgents/ai.oyster.chrome-cdp-9222.plist"
  ```
- 方案B: VNC 远程登录 (vnc://192.168.4.63)

### 1b: 跑第一个真实任务
用 twitter_poster.py 发一条测试推文 (dry-run):
```bash
cd ~/Downloads/twitter-poster
python3 twitter_poster.py post "test" --dry-run --cdp-endpoint http://127.0.0.1:9222
```

---

## Part 2: 错误反馈机制 (Mac-2 自动检测 + 上报 + 修复)

### 框架 (Opus 搭)

```
Mac-2 健康检查脚本 (每 5min)
  │
  ├── 检测: Chrome CDP 还活着吗? (curl /json/version)
  ├── 检测: launchd 服务状态正常?
  ├── 检测: 内存/磁盘/CPU 异常?
  ├── 检测: SSH tunnel 还通?
  │
  ├── 问题分类:
  │   ├── SELF_HEAL: 可自动修复 (重启服务、清理磁盘)
  │   ├── REPORT: 需要上报 (写 issue_inbox + claude-mem)
  │   └── CRITICAL: 紧急 (写 issue_inbox + 发 Telegram 通知)
  │
  └── 自动修复:
      ├── Chrome 挂了 → launchctl unload/load 重启
      ├── 内存不够 → 清理 Chrome 缓存
      └── tunnel 断了 → Mac-1 侧 launchd 自动重连
```

### 具体要求 (副元帅补充细节并实现)

1. 在 Mac-2 上创建 `~/health-check.sh`:
   - 检查 CDP 9222 和 9223 端口
   - 检查 launchd 服务状态
   - 检查内存使用 (>80% 告警)
   - 检查磁盘 (>90% 告警)
   - 输出: JSON 格式 `{"status": "ok|warn|error", "checks": {...}, "timestamp": "..."}`
   - 自动修复: Chrome 挂了自动 launchctl 重启

2. 在 Mac-2 创建 launchd plist: 每 5 分钟运行 health-check.sh

3. 健康日志写到 `~/health-check.log`

4. 错误上报:
   - 写入 `~/Library/Application Support/CodexClaudeSync/issue_inbox.txt` (Mac-1 可读)
   - 或: 写到共享文件，Mac-1 side 通过 SSH 定期拉取

### 验收标准
- [ ] health-check.sh 在 Mac-2 运行，输出 JSON
- [ ] Chrome CDP 挂了能自动重启
- [ ] 错误日志可从 Mac-1 查看
- [ ] launchd 定时任务运行 (每 5min)

---

## Part 3: 账户管理体系 (统一 key/credential)

### 框架 (Opus 搭)

```
~/.oyster-keys/           ← 集中存放所有 credential
├── twitter.env           ← Twitter 相关 (RapidAPI, xAI)
├── openai.env            ← OpenAI/Codex
├── anthropic.env         ← Claude API
├── aws.env               ← AWS access key
├── openclaw.env          ← OpenClaw proxy keys
├── github.env            ← GitHub token
├── telegram.env          ← TG bot token
├── discord.env           ← Discord bot token
├── kimi.env              ← Kimi K2 API
└── master.env            ← 汇总所有 key 的 source file
```

### 具体要求 (副元帅补充细节并实现)

1. **审计现有 key 散落位置**:
   ```bash
   # 找所有 .env 文件
   find ~/Downloads ~/clawd ~/.twitter-poster ~/.openclaw -name "*.env" -o -name ".env*" 2>/dev/null
   # 找 shell 环境变量里的 key
   env | grep -i "key\|token\|secret\|api" | grep -v PATH
   ```

2. **创建 `~/.oyster-keys/` 目录结构**

3. **收归所有 key 到标准位置** (不删原文件，先复制)

4. **创建 `~/.oyster-keys/load.sh`** — source 一次加载所有 key:
   ```bash
   #!/bin/bash
   for f in ~/.oyster-keys/*.env; do
     [ -f "$f" ] && set -a && source "$f" && set +a
   done
   ```

5. **同步到 Mac-2** (rsync，排除不需要的):
   ```bash
   rsync -av ~/.oyster-keys/ howardlee@192.168.4.63:~/.oyster-keys/
   ```

### 验收标准
- [ ] `~/.oyster-keys/` 目录存在，含按服务分类的 .env 文件
- [ ] `source ~/.oyster-keys/load.sh` 可加载所有 key
- [ ] Mac-2 同步了 key
- [ ] 不破坏现有 .env 文件 (只新增，不删除原位置)

---

## 注意
- Mac-2 用户名是 howardlee (不是 howardli)
- 所有 Mac-2 操作通过 SSH 完成: `ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63`
- 或用 SSH config 简称: `ssh mac2-cdp`
- key 文件权限必须 600: `chmod 600 ~/.oyster-keys/*.env`
- 不要把真实 key 写进 claude-mem 或 handoff.md
