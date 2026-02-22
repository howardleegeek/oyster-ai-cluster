---
task_id: S03-monitor
project: dispatch
priority: 2
depends_on: []
modifies: ["dispatch/monitor.py"]
executor: glm
---

# API 用量监控 monitor.py

## 目标
创建 dispatch/monitor.py，查询各 AI API 余额/用量，输出表格，持久化到 SQLite，低阈值告警。

## API Key 来源
按优先级读取：
1. 环境变量: ANTHROPIC_API_KEY, GLM_API_KEY, MINIMAX_API_KEY, OPENAI_API_KEY
2. 文件: ~/.oyster-keys/<provider> (内容为 key 字符串)
3. 找不到就跳过该 provider

## Provider 查询

### GLM (智谱)
```
GET https://open.bigmodel.cn/api/paas/v4/finance/balance
Header: Authorization: Bearer <key>
Response: {"success": true, "data": {"granted_balance": 100.0, ...}}
```

### MiniMax
尝试查余额 API，查不到就跳过。

### Anthropic / OpenAI
这两个是 client 端订阅 (Claude Code / Codex CLI)，没有 API 余额概念。
处理方式：
- 如果设了环境变量 ANTHROPIC_BUDGET / OPENAI_BUDGET (数字)，用它做总预算
- 从 dispatch.db 统计该 provider 的已完成任务数作为"已用"
- 没设 BUDGET 就显示 "N/A (client subscription)"

## 输出格式
```
=== AI API Usage Monitor ===
Provider        Status    Used        Remaining   Alert
─────────────────────────────────────────────────────
Anthropic       ℹ️ N/A    (subscription)
GLM (智谱)      ⚠️ LOW    ¥180.00     ¥20.00      < 10%
MiniMax         ✅ OK     ¥50.00      ¥950.00
Codex/OpenAI    ℹ️ N/A    (subscription)
─────────────────────────────────────────────────────
Last check: 2026-02-12 16:30:00
```

## 数据库
文件: dispatch/monitor.db

```sql
CREATE TABLE IF NOT EXISTS usage_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    used REAL,
    remaining REAL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'ok'
);
CREATE INDEX IF NOT EXISTS idx_snap_ts ON usage_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_snap_provider ON usage_snapshots(provider);
```

## 告警阈值
- remaining >= 10% → OK (✅)
- 5% <= remaining < 10% → WARNING (⚠️)
- remaining < 5% → CRITICAL (🚨)
- API 不可达 → ERROR (❌)
- 无余额概念 → INFO (ℹ️)

## CLI 接口
```bash
python3 monitor.py check     # 查一次，输出表格
python3 monitor.py watch     # 每 300 秒循环查询
python3 monitor.py history   # 最近 24h 趋势
```

## 约束
- Python 3.9+
- 只用标准库 (urllib) + 可选 requests
- 不存储 API key 到数据库
- 查不到的 provider 跳过不报错
- 文件: dispatch/monitor.py (单文件)

## 验收标准
- [ ] `python3 monitor.py check` 不报错，输出表格
- [ ] GLM 余额查询正确（如果有 key）
- [ ] 无 key 的 provider 显示 skip 而非报错
- [ ] `python3 monitor.py history` 显示历史数据
- [ ] monitor.db 自动创建且有数据
