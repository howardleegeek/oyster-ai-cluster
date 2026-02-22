# ClawPhones Sprint 14-16 Gap Completion Spec

> Opus 战略 spec → dispatch GLM 并发执行
> 工作目录: `~/.openclaw/workspace/`

---

## 任务 A: Sprint 14 — Relay Task Distribution (GCP codex-node-1)

### 背景
TaskMarketService (iOS/Android) + Backend 6 endpoints 已完成，但 Relay (`server.s11-6.js`) 有 0 task refs。
需要给 Relay 加 task 分发能力，让节点可以通过 Relay 发现/领取/提交任务。

### 具体要求

在 `server.s11-6.js` 尾部（现有 community 端点之后）新增 6 个端点：

1. `POST /v1/tasks/distribute` — Backend 推送新任务到 Relay
   - Body: `{ task_id, type, location: {lat, lon}, radius_km, requirements, reward, expires_at }`
   - 存入 `data/tasks.json`，按 H3 cell (resolution 9) 索引
   - 返回 `{ ok: true, task_id }`

2. `GET /v1/tasks/available?lat=X&lon=Y&radius=Z` — 节点查询附近可领取任务
   - 用 H3 cellsToMultiPolygon 或 kRing 找邻近 cell
   - 只返回 status=open 且未过期的任务
   - 返回 `{ tasks: [...] }`

3. `POST /v1/tasks/:id/claim` — 节点领取任务
   - Body: `{ node_id }`
   - 检查任务 status=open，原子设为 claimed，记录 claimed_by + claimed_at
   - 防重复领取：已被领取返回 409
   - 返回 `{ ok: true, task }`

4. `POST /v1/tasks/:id/heartbeat` — 节点报告进度
   - Body: `{ node_id, progress_pct, status_msg }`
   - 更新任务 last_heartbeat
   - 返回 `{ ok: true }`

5. `POST /v1/tasks/:id/results` — 节点提交结果
   - Body: `{ node_id, result_data, files: [] }`
   - 设任务 status=completed，追加到 `data/task-results.jsonl`
   - 返回 `{ ok: true }`

6. `GET /v1/tasks/stats` — 任务统计
   - 返回 `{ total, open, claimed, completed, by_cell: {...} }`

### 数据文件
- `data/tasks.json` — `{ tasks: { [task_id]: { ...task, h3_cell, status, claimed_by, ... } } }`
- `data/task-results.jsonl` — 每行一个 JSON result

### 现有代码接入点
- **复用**: `readJson()`/`writeJson()` helper, `json()` response helper, H3 `latLngToCell()` (已有)
- **参考**: community 端点的 routing pattern (`if (method === 'POST' && url.pathname === '...')`)
- **不要碰**: 现有 vision/community/push/ws 端点

### 边界情况
- 任务过期：claim 时检查 expires_at
- 双重 claim：原子读写，先读 status 再改
- 空查询：lat/lon 缺失返回 400
- node_id 校验：非空字符串即可

### 验收标准
- [ ] 6 个端点全部可用 (curl 测试)
- [ ] tasks.json 正确读写
- [ ] H3 geo-query 返回正确结果
- [ ] claim 防重复 (409)

---

## 任务 B: Sprint 15 — Edge Compute Relay + Backend (GCP glm-node-2)

### 背景
EdgeComputeService (iOS/Android) 客户端已完成，但 Relay 和 Backend 都缺 edge compute 端点。

### B1: Relay 端点 (在 server.s11-6.js 新增)

1. `POST /v1/compute/nodes/register` — 注册算力节点
   - Body: `{ node_id, capabilities: { cpu_cores, memory_mb, gpu, ml_models: [], battery_pct } }`
   - 存入 `data/compute-nodes.json`
   - 返回 `{ ok: true, node_id }`

2. `GET /v1/compute/jobs/poll?node_id=X` — 节点轮询待处理任务
   - 匹配节点 capabilities vs job requirements
   - 返回 `{ job: {...} | null }`

3. `POST /v1/compute/jobs/:id/claim` — 领取计算任务
   - Body: `{ node_id }`
   - 防重复领取 (409)
   - 返回 `{ ok: true, job }`

4. `POST /v1/compute/jobs/:id/heartbeat` — 进度上报
   - Body: `{ node_id, progress_pct, metrics: { cpu_usage, memory_usage } }`
   - 返回 `{ ok: true }`

5. `POST /v1/compute/jobs/:id/results` — 提交结果
   - Body: `{ node_id, output_data, execution_time_ms, metrics }`
   - 追加到 `data/compute-results.jsonl`
   - 返回 `{ ok: true }`

6. `GET /v1/compute/nodes/online` — 在线算力节点列表
   - 过滤 last_heartbeat > 5min 前的为离线
   - 返回 `{ nodes: [...], total_capacity: {...} }`

7. `POST /v1/compute/jobs` — 创建计算任务 (管理/买方 API)
   - Body: `{ type, requirements: { min_memory_mb, gpu_required, ml_model }, input_data, priority, reward }`
   - 存入 `data/compute-jobs.json`
   - 返回 `{ ok: true, job_id }`

8. `GET /v1/compute/stats` — 算力统计
   - 返回 `{ nodes_online, jobs_total, jobs_pending, jobs_completed, total_compute_hours }`

### B2: Backend 端点 (在 proxy/server.py 新增)

在现有 `/v1/tasks/*` 端点后面新增 8 个 FastAPI 端点：

1. `POST /v1/compute/jobs` — 创建计算任务
   - 需要认证 (依赖 current_user)
   - 创建 compute_jobs 表记录
   - 转发给 Relay

2. `GET /v1/compute/jobs/available` — 查询可用任务
   - 按节点能力过滤

3. `POST /v1/compute/jobs/{job_id}/accept` — 接受任务
   - 乐观锁防重复

4. `POST /v1/compute/jobs/{job_id}/results` — 提交结果
   - 验证节点是否是 claimed_by

5. `GET /v1/compute/jobs/mine` — 我的计算任务
   - 按 node_id 或 user_id 查询

6. `GET /v1/compute/nodes/register` → `POST /v1/compute/nodes/register` — 注册节点
   - 关联 user_id

7. `GET /v1/compute/stats` — 统计
   - 全局 + 个人

8. `GET /v1/compute/earnings` — 算力收益
   - 按时段汇总

### 数据文件 (Relay)
- `data/compute-nodes.json` — `{ nodes: { [node_id]: { capabilities, last_heartbeat, status } } }`
- `data/compute-jobs.json` — `{ jobs: { [job_id]: { type, requirements, status, claimed_by, ... } } }`
- `data/compute-results.jsonl` — 结果日志

### Backend DB (新增表)
```sql
CREATE TABLE IF NOT EXISTS compute_jobs (
    id TEXT PRIMARY KEY,
    creator_id TEXT NOT NULL,
    type TEXT NOT NULL,
    requirements TEXT, -- JSON
    input_data TEXT, -- JSON
    status TEXT DEFAULT 'pending', -- pending/claimed/running/completed/failed
    claimed_by TEXT,
    claimed_at TEXT,
    completed_at TEXT,
    result_data TEXT, -- JSON
    priority INTEGER DEFAULT 0,
    reward REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS compute_nodes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    capabilities TEXT, -- JSON
    status TEXT DEFAULT 'offline',
    last_heartbeat TEXT,
    total_jobs_completed INTEGER DEFAULT 0,
    total_compute_hours REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### 现有代码接入点
- **Relay**: 同任务 A 的 pattern，加在 task 端点后面
- **Backend**: 参考 `/v1/tasks/*` 端点的模式，复用 `get_current_user()`, `get_db()`, rate limiter
- **不要碰**: 现有 community/push/task 端点

### 边界情况
- 节点离线：heartbeat 超 5min 标记 offline，释放其 claimed 任务
- GPU required 但无 GPU 节点：返回空
- 大文件 result：限制 result_data < 10MB
- 并发 claim：乐观锁/原子操作

### 验收标准
- [ ] Relay 8 个端点可用
- [ ] Backend 8 个端点可用
- [ ] DB 表自动创建
- [ ] 节点注册 → 轮询 → 领取 → 提交全链路

---

## 任务 C: Sprint 16 — NotificationSettingsView.swift (GCP codex-node-1, 与 A 并发)

### 背景
PushNotificationService 和 Backend preferences API 已就绪，缺集中设置 UI。

### 具体要求

新建 `ios/ClawPhones/Views/NotificationSettingsView.swift`:

```
参考: CommunitySettingsView.swift 的 Form 模式
```

功能:
1. **通知类别开关** — Form Section
   - 社区警报 (communityAlerts: Bool)
   - 任务通知 (taskNotifications: Bool)
   - 计算任务 (computeAlerts: Bool)
   - 系统更新 (systemUpdates: Bool)

2. **免打扰时段** — Form Section
   - 开关 + 开始/结束时间 DatePicker
   - quietHoursEnabled, quietStart, quietEnd

3. **声音与振动** — Form Section
   - soundEnabled: Bool
   - vibrationEnabled: Bool
   - alertSound: Picker (default, bell, chime, silent)

4. **保存** — 调用 PushNotificationService.updatePreferences()
   - 用 @State 管理本地状态
   - onAppear 加载当前设置
   - onChange 自动保存 (debounce 500ms)

### 现有代码接入点
- 复用: `PushNotificationService` 的 getPreferences / updatePreferences
- 参考: `CommunitySettingsView.swift` 的 Form + Toggle 模式
- Xcode project: 需要在 project.pbxproj 新增文件引用

### 验收标准
- [ ] 文件存在且语法正确
- [ ] 使用 SwiftUI Form + Toggle + DatePicker
- [ ] 调用 PushNotificationService

---

## 任务 D: Sprint 16 — LiveAlertFeedView.swift (GCP glm-node-2, 与 B 并发)

### 背景
WebSocketService 和 Relay `/v1/ws/alerts` 已就绪，缺实时 feed UI。

### 具体要求

新建 `ios/ClawPhones/Views/LiveAlertFeedView.swift`:

```
参考: AlertHistoryView.swift (列表模式) + WebSocketService (连接模式)
```

功能:
1. **实时 WebSocket 连接** — onAppear 连接 `/v1/ws/alerts`
   - 用 WebSocketService.connect()
   - 显示连接状态指示器 (绿点=在线, 红点=断开)

2. **Alert Feed 列表** — LazyVStack (新消息在顶部)
   - 每条: 类型图标 + 标题 + 时间 + 距离
   - 类型: motion, person, vehicle, sound, community
   - 点击进入 AlertDetailView

3. **过滤器** — 顶部 Picker/SegmentedControl
   - All / Motion / Person / Vehicle / Community

4. **空状态** — 无 alert 时显示 "No alerts yet"

5. **断线重连** — WebSocket 断开时自动重连 (5s interval)

### 现有代码接入点
- 复用: `WebSocketService` 的 connect/disconnect/onMessage
- 复用: `AlertEvent` model (已有)
- 参考: `AlertHistoryView.swift` 的列表布局
- Xcode project: 需要在 project.pbxproj 新增文件引用

### 验收标准
- [ ] 文件存在且语法正确
- [ ] 使用 WebSocketService 连接
- [ ] LazyVStack 显示实时 alerts
- [ ] 过滤器工作正常

---

## 任务 E: Relay Push Preferences (附加到任务 A/B 的节点)

在 `server.s11-6.js` 新增 2 个端点:

1. `GET /v1/push/preferences?node_id=X` — 获取推送偏好
   - 从 `data/push-preferences.json` 读取
   - 返回 `{ preferences: { communityAlerts, taskNotifications, ... } }`

2. `PUT /v1/push/preferences` — 更新推送偏好
   - Body: `{ node_id, preferences: {...} }`
   - 存入 `data/push-preferences.json`
   - 返回 `{ ok: true }`

---

## Dispatch 分配

| 任务 | 节点 | 文件 | 预计行数 |
|------|------|------|---------|
| A (Task Relay) + C (NotificationSettings) + E (Push Prefs) | codex-node-1 | server.s11-6.js + NotificationSettingsView.swift | ~400 |
| B (Edge Compute) + D (LiveAlertFeed) | glm-node-2 | server.s11-6.js + proxy/server.py + LiveAlertFeedView.swift | ~600 |

**并发执行**: 两台 GCP 同时跑，互不冲突 (不改同一文件的同一区域)

**注意**: 任务 A 和 B 都改 server.s11-6.js，但 A 加 task 端点，B 加 compute 端点。
为避免冲突：
- 节点 1 (任务 A): 在文件尾部 community 端点后加 task + push-preferences 端点
- 节点 2 (任务 B): **不改 Relay 文件**，只改 proxy/server.py + 新建 LiveAlertFeedView.swift
- B 的 Relay compute 端点由节点 1 在 A 完成后追加 (串行)
- 或者: 节点 2 把 Relay compute 部分输出为独立 patch 文件 `compute-relay-patch.js`

**最终合并**: 两边都完成后，手动 merge relay 代码 + commit
