## 任务: Mac-2 执行节点初始化 + Mac-1 SSH 隧道建立

### 背景
Mac-1 内存超负荷 (~20GB)，需要把 Chrome CDP 浏览器实例迁移到 Mac-2 (192.168.4.63)。
使用 SSH 隧道方案 — Mac-1 代码零改动，通过 SSH 端口转发把 localhost:9222/9223/9224 路由到 Mac-2。

### Mac-2 SSH 连接
```bash
ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63
```

### Mac-2 当前状态 (已确认)
- Node.js v25.6.0 ✅
- Homebrew 5.0.14 ✅
- 防睡眠已配置 (sleep 0, caffeinate, nosleep plist) ✅
- 已有 LaunchAgents: ai.openclaw.node.plist, ai.oyster.openclaw.gateway-tunnel.plist ✅

### Mac-1 当前 Chrome CDP 进程
- Port 9222: `--user-data-dir=/Users/howardli/Library/Application Support/Google/Chrome-CodexCDP` (Twitter 主号 @ClawGlasses)
- Port 9223: `--user-data-dir=/Users/howardli/Library/Application Support/Google/Chrome-CodexCDP-puffy` (Puffy)
- Port 9224: 目前未运行 (曾经用于 puffy)

### 具体要求

#### Step 1: Mac-2 Chrome CDP 启动脚本
在 Mac-2 上通过 SSH 创建文件:

1. 创建 `~/chrome-cdp-start.sh`:
```bash
#!/bin/bash
# Chrome CDP instances for Twitter automation
# Port 9222: @ClawGlasses + delegates
# Port 9223: @puffy_ai / UBS

start_cdp() {
    local port=$1
    local datadir=$2

    # Check if already running
    if lsof -nP -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
        echo "Port $port already in use, skipping"
        return 0
    fi

    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
        --remote-debugging-address=127.0.0.1 \
        --remote-debugging-port=$port \
        --user-data-dir="$datadir" \
        --no-first-run \
        --no-default-browser-check \
        --disable-background-networking \
        --headless=new &

    echo "Started Chrome CDP on port $port (PID: $!)"
}

start_cdp 9222 "$HOME/chrome-cdp-9222"
start_cdp 9223 "$HOME/chrome-cdp-9223"
```

2. `chmod +x ~/chrome-cdp-start.sh`

3. 创建 Mac-2 LaunchAgent `~/Library/LaunchAgents/ai.oyster.chrome-cdp-9222.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.oyster.chrome-cdp-9222</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Google Chrome.app/Contents/MacOS/Google Chrome</string>
        <string>--remote-debugging-address=127.0.0.1</string>
        <string>--remote-debugging-port=9222</string>
        <string>--user-data-dir=/Users/howardlee/chrome-cdp-9222</string>
        <string>--no-first-run</string>
        <string>--no-default-browser-check</string>
        <string>--disable-background-networking</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/chrome-cdp-9222.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/chrome-cdp-9222.log</string>
</dict>
</plist>
```

4. 同样创建 `ai.oyster.chrome-cdp-9223.plist` (改端口和 user-data-dir)

5. 加载 LaunchAgents:
```bash
launchctl load ~/Library/LaunchAgents/ai.oyster.chrome-cdp-9222.plist
launchctl load ~/Library/LaunchAgents/ai.oyster.chrome-cdp-9223.plist
```

#### Step 2: 迁移 Chrome Profile (Mac-1 → Mac-2)

从 Mac-1 rsync Chrome 登录态到 Mac-2:

```bash
# 在 Mac-1 上执行
rsync -avz "/Users/howardli/Library/Application Support/Google/Chrome-CodexCDP/" \
  howardlee@192.168.4.63:/Users/howardlee/chrome-cdp-9222/

rsync -avz "/Users/howardli/Library/Application Support/Google/Chrome-CodexCDP-puffy/" \
  howardlee@192.168.4.63:/Users/howardlee/chrome-cdp-9223/
```

注意: rsync 时 Mac-2 的 Chrome CDP 不要在运行 (先 unload launchd)。
所以正确顺序: rsync profile → 然后 load launchd 启动 Chrome。

#### Step 3: Mac-1 SSH Config + 隧道

1. 创建/更新 Mac-1 的 `~/.ssh/config`:
```
Host mac2-cdp
    HostName 192.168.4.63
    User howardlee
    IdentityFile ~/.ssh/howard-mac2
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

2. 创建 Mac-1 LaunchAgent `~/Library/LaunchAgents/ai.oyster.cdp-tunnel.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.oyster.cdp-tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/ssh</string>
        <string>-N</string>
        <string>-o</string><string>ExitOnForwardFailure=yes</string>
        <string>-o</string><string>ServerAliveInterval=60</string>
        <string>-o</string><string>ServerAliveCountMax=3</string>
        <string>-L</string><string>9222:127.0.0.1:9222</string>
        <string>-L</string><string>9223:127.0.0.1:9223</string>
        <string>mac2-cdp</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/cdp-tunnel.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/cdp-tunnel.log</string>
</dict>
</plist>
```

3. 切换步骤 (在 Mac-1 上):
```bash
# 1. 先杀 Mac-1 本地 CDP Chrome
pkill -f "remote-debugging-port=9222"
pkill -f "remote-debugging-port=9223"
sleep 3

# 2. 确认端口释放
lsof -nP -iTCP:9222 -sTCP:LISTEN || echo "Port 9222 free"
lsof -nP -iTCP:9223 -sTCP:LISTEN || echo "Port 9223 free"

# 3. 启动隧道
launchctl load ~/Library/LaunchAgents/ai.oyster.cdp-tunnel.plist
sleep 3

# 4. 验证隧道连通
curl -s http://127.0.0.1:9222/json/version | python3 -m json.tool
curl -s http://127.0.0.1:9223/json/version | python3 -m json.tool
```

### 文件
- Mac-2: `~/chrome-cdp-start.sh` (新建)
- Mac-2: `~/Library/LaunchAgents/ai.oyster.chrome-cdp-9222.plist` (新建)
- Mac-2: `~/Library/LaunchAgents/ai.oyster.chrome-cdp-9223.plist` (新建)
- Mac-1: `~/.ssh/config` (新建)
- Mac-1: `~/Library/LaunchAgents/ai.oyster.cdp-tunnel.plist` (新建)

### 验收标准
- [ ] Mac-2 Chrome CDP 9222 和 9223 在运行 (launchd 管理)
- [ ] Mac-1 SSH 隧道建立: `curl http://127.0.0.1:9222/json/version` 返回 Mac-2 Chrome 信息
- [ ] Mac-1 SSH 隧道建立: `curl http://127.0.0.1:9223/json/version` 返回 Mac-2 Chrome 信息
- [ ] Mac-1 本地 Chrome CDP 进程已停止
- [ ] Mac-1 端口 9222/9223 由 ssh 进程监听 (不是 Chrome)

### 注意
- Mac-2 SSH: `ssh -i ~/.ssh/howard-mac2 howardlee@192.168.4.63`
- Mac-2 用户名是 `howardlee` (不是 `howardli`)
- Chrome Profile rsync 必须在 Chrome 启动前完成
- Mac-1 必须先杀 Chrome 再启隧道，否则端口冲突
- 不要修改 twitter_poster.py 或任何 Python 代码！SSH 隧道方案就是零代码改动
- Mac-2 Chrome 如果用 --headless=new 模式，不会显示 GUI 窗口 (节省内存)。但如果需要手动登录 Twitter，去掉 headless 参数。
- 先不加 --headless，等确认 Twitter 登录态保留后再加
