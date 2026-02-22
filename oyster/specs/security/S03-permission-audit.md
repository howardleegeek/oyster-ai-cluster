---
task_id: SEC-006
project: security
priority: 2
depends_on: []
modifies: []
executor: glm
---

## 目标
全面扫描 ~/Downloads/ 和 ~/.oyster-keys/ 下所有敏感文件，修复权限为 600。

## 步骤
1. 扫描所有敏感文件：
   ```bash
   find ~/Downloads ~/.oyster-keys -type f \( \
     -name "*.key" -o -name "*.pem" -o -name "*.p12" -o \
     -name ".env" -o -name ".env.*" -o \
     -name "credentials.json" -o -name "*secret*" \
   \) ! -path "*/node_modules/*" ! -path "*/.venv/*" -exec ls -la {} \;
   ```
2. 找出权限不是 600 的文件：
   ```bash
   find ~/Downloads ~/.oyster-keys -type f \( \
     -name "*.key" -o -name "*.pem" -o -name ".env" -o -name ".env.*" \
   \) ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -perm 600
   ```
3. 修复权限：
   ```bash
   find ~/Downloads ~/.oyster-keys -type f \( \
     -name "*.key" -o -name "*.pem" -o -name ".env" -o -name ".env.*" \
     -o -name "credentials.json" \
   \) ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -perm 600 -exec chmod 600 {} \;
   ```
4. 生成审计报告到 `~/security-audit-$(date +%Y%m%d).txt`

## 验收标准
- [ ] 审计报告生成在 `~/security-audit-YYYYMMDD.txt`
- [ ] 报告中所有文件权限均为 `-rw-------` (600)
- [ ] `~/.oyster-keys/` 目录权限为 700

## 不要做
- 不删除任何文件
- 不修改文件内容
- 不动 node_modules 或 .venv 内的文件
