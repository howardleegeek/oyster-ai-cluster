---
task_id: SEC-007
project: security
priority: 3
depends_on: ["SEC-006"]
modifies: ["~/bin/security-scan.sh"]
executor: glm
---

## 目标
创建每日自动安全扫描脚本，检测新出现的私钥暴露和权限问题。

## 步骤
1. 创建 `~/bin/security-scan.sh`：
   ```bash
   #!/bin/bash
   set -euo pipefail
   LOG_DIR=~/logs/security
   mkdir -p "$LOG_DIR"
   LOG="$LOG_DIR/scan-$(date +%Y%m%d).log"
   ALERT=0

   echo "=== Security Scan $(date) ===" > "$LOG"

   # 1. 检查 Downloads 是否有新的私钥文件
   echo "--- Exposed keys in Downloads ---" >> "$LOG"
   FOUND=$(find ~/Downloads -maxdepth 2 -type f \( -name "*.key" -o -name "*.pem" \) 2>/dev/null | wc -l)
   if [ "$FOUND" -gt 0 ]; then
     find ~/Downloads -maxdepth 2 -type f \( -name "*.key" -o -name "*.pem" \) >> "$LOG"
     ALERT=1
   fi

   # 2. 检查权限不合规的敏感文件
   echo "--- Permission issues ---" >> "$LOG"
   BAD=$(find ~/Downloads ~/.oyster-keys -type f \( -name "*.key" -o -name ".env" -o -name ".env.*" \) \
     ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -perm 600 2>/dev/null | wc -l)
   if [ "$BAD" -gt 0 ]; then
     find ~/Downloads ~/.oyster-keys -type f \( -name "*.key" -o -name ".env" -o -name ".env.*" \) \
       ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -perm 600 >> "$LOG"
     ALERT=1
   fi

   # 3. 检查 git 仓库中是否有已跟踪的敏感文件
   echo "--- Tracked secrets in repos ---" >> "$LOG"
   for repo in ~/Downloads/*/.git; do
     [ -d "$repo" ] || continue
     TRACKED=$(git -C "$repo/.." ls-files | grep -E '\.(env|key|pem)$' 2>/dev/null || true)
     if [ -n "$TRACKED" ]; then
       echo "REPO: $repo" >> "$LOG"
       echo "$TRACKED" >> "$LOG"
       ALERT=1
     fi
   done

   # 4. 总结
   if [ "$ALERT" -eq 1 ]; then
     echo "SECURITY ALERT: Issues found. See $LOG"
   else
     echo "All clear." >> "$LOG"
   fi
   ```
2. `chmod +x ~/bin/security-scan.sh`
3. 添加 launchd plist（macOS 推荐用 launchd 而非 crontab）：
   创建 `~/Library/LaunchAgents/com.oyster.security-scan.plist`
   每天早上 9 点执行
4. `launchctl load ~/Library/LaunchAgents/com.oyster.security-scan.plist`
5. 手动运行一次验证：`~/bin/security-scan.sh`

## 验收标准
- [ ] `~/bin/security-scan.sh` 存在且可执行
- [ ] 手动运行生成日志到 `~/logs/security/scan-YYYYMMDD.log`
- [ ] launchd 任务已加载：`launchctl list | grep security-scan`

## 不要做
- 不修改任何源代码
- 不删除发现的文件（只报告）
- 不用 crontab（macOS 用 launchd）
