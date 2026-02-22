# 共享大脑体系 — 让所有节点都有记忆和上下文

> 核心问题: Mac-1 有完整的记忆(claude-mem) + 配置(CLAUDE.md) + 密钥(oyster-keys),
> 但 GCP/Mac-2 上的 GLM/Codex session 什么都不知道。

---

## 一、当前的断裂

```
Mac-1 (Opus 大脑)           →  dispatch spec  →  GCP Worker
├─ claude-mem (3670+ obs)                        ├─ 什么都不知道
├─ CLAUDE.md (架构决策)                           ├─ 不知道项目规范
├─ specs/ (100 个 spec)                          ├─ 只看到一个 spec.md
├─ memory/ (4 topic files)                       ├─ 不知道历史教训
├─ .oyster-keys/ (7 密钥)                        ├─ 没有 API 密钥
└─ QMD (8 collections)                           └─ 不能搜索代码库
```

**结果**: 每个 GLM session 收到的只是一段 spec 文本。没有项目上下文, 没有架构决策, 没有历史教训。
就像让一个新人只看一张需求卡, 不给他看代码库、不给他看 wiki、不让他问老员工。

---

## 二、解决方案: Context Pack 注入

不搞复杂的远程 API 或数据库同步。**直接把 worker 需要的上下文打包进 spec 里。**

### 为什么不搞远程 API?

| 方案 | 优点 | 缺点 |
|------|------|------|
| Mac-1 HTTP API | 实时查询 | Mac-1 要开端口, 安全风险, 网络依赖 |
| rsync claude-mem.db | 完整数据 | 96MB 每次同步, GCP 需要 claude-mem 插件 |
| S3/GCS 共享 | 跨节点 | 额外成本, 延迟, 需要认证 |
| **Context Pack 注入** | **简单, 零依赖** | **上下文有限** |

### Context Pack 注入方案

dispatch.py 在发送 spec 到 worker 之前，**自动拼接上下文**:

```python
def build_enriched_spec(project, task_id, spec_content):
    """把 spec 变成一个自包含的、有上下文的工作包"""

    context_pack = []

    # 1. 项目级 CLAUDE.md (架构决策、编码规范)
    project_claude_md = load_project_claude_md(project)
    if project_claude_md:
        context_pack.append(f"## Project Instructions\n{project_claude_md}")

    # 2. 相关 claude-mem 记忆 (按项目 + 关键词搜索)
    memories = search_claude_mem(project, task_id)
    if memories:
        context_pack.append(f"## Project Memory (Recent Decisions)\n{memories}")

    # 3. 共享上下文 (如果有 SHARED_CONTEXT.md)
    shared_ctx = load_shared_context(project, task_id)
    if shared_ctx:
        context_pack.append(f"## Shared Context\n{shared_ctx}")

    # 4. 其他任务的状态 (避免冲突)
    sibling_status = get_sibling_task_status(project, task_id)
    if sibling_status:
        context_pack.append(f"## Other Tasks Status\n{sibling_status}")

    # 5. 节点特定配置 (API 密钥路径等)
    node_config = get_node_env_config(task_id)
    if node_config:
        context_pack.append(f"## Environment\n{node_config}")

    # 拼接
    enriched = "\n\n---\n\n".join(context_pack)
    enriched += f"\n\n---\n\n## Task Spec\n\n{spec_content}"

    return enriched
```

### 各层上下文的具体内容

#### 层 1: Project CLAUDE.md (每个项目通用)

```
~/Downloads/<project>/CLAUDE.md 或 ~/Downloads/specs/<project>/CLAUDE.md
```

包含:
- 编码规范 (命名、文件结构、import 风格)
- 技术栈 (Python 3.11, FastAPI, React 18, PostgreSQL)
- 安全要求 (不硬编码 key, 输入校验)
- 目录结构 (哪个文件在哪)

**大小**: ~2-3KB, ~1000 token

#### 层 2: claude-mem 记忆提取

```python
def search_claude_mem(project, task_id):
    """从 claude-mem 提取相关记忆"""
    import sqlite3

    db_path = Path.home() / '.claude-mem' / 'claude-mem.db'
    if not db_path.exists():
        return ""

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # 按项目搜索最近的决策和发现
    rows = conn.execute('''
        SELECT type, narrative, created_at_epoch
        FROM observations
        WHERE project LIKE ? AND type IN ('decision', 'discovery', 'bugfix')
        ORDER BY created_at_epoch DESC
        LIMIT 10
    ''', (f'%{project}%',)).fetchall()

    conn.close()

    if not rows:
        return ""

    lines = []
    for row in rows:
        ts = datetime.fromtimestamp(row['created_at_epoch']).strftime('%m/%d')
        lines.append(f"- [{row['type']}] {ts}: {row['narrative'][:200]}")

    return "\n".join(lines)
```

**大小**: ~1-2KB, ~500 token (10 条记忆, 每条 200 字符截断)

#### 层 3: 智能 SHARED_CONTEXT 提取

替代 "把完整 SHARED_CONTEXT 塞给每个 session" 的做法:

```python
def load_shared_context(project, task_id):
    """按 task spec 内容智能提取相关的共享上下文章节"""

    shared_path = Path.home() / 'Downloads' / 'specs' / project / 'SHARED_CONTEXT.md'
    if not shared_path.exists():
        return ""

    # 读 spec 提取关键词
    spec_keywords = extract_keywords(task_spec)

    # SHARED_CONTEXT 按 ## 标题分章节
    sections = parse_sections(shared_path.read_text())

    # 只保留和 spec 相关的章节
    relevant = []
    for section in sections:
        if any(kw in section['title'].lower() or kw in section['body'].lower()
               for kw in spec_keywords):
            relevant.append(section['full_text'])

    return "\n\n".join(relevant[:5])  # 最多 5 个章节
```

**大小**: ~1-3KB, ~500-1500 token (vs 之前的 5000 token)

#### 层 4: 兄弟任务状态

```python
def get_sibling_task_status(project, task_id):
    """告诉这个 worker 其他 worker 在做什么, 避免冲突"""

    db_path = Path.home() / 'Downloads' / 'dispatch' / 'dispatch.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    rows = conn.execute('''
        SELECT id, status, node, spec_file FROM tasks
        WHERE project = ? AND id != ?
        ORDER BY id
    ''', (project, task_id)).fetchall()

    conn.close()

    lines = ["Other tasks in this project:"]
    for row in rows:
        spec_name = Path(row['spec_file']).stem
        lines.append(f"- {row['id']} ({spec_name}): {row['status']} on {row['node'] or 'unassigned'}")

    lines.append("")
    lines.append("IMPORTANT: If your task creates files that other tasks might also create,")
    lines.append("prefix with your task ID to avoid conflicts. Don't modify files owned by other tasks.")

    return "\n".join(lines)
```

**大小**: ~500 bytes, ~200 token

#### 层 5: 环境配置

```python
def get_node_env_config(node_name):
    """节点特定的环境信息"""

    configs = {
        "mac1": "Environment: macOS, Python 3.11, Node 22. Local execution.",
        "mac2": "Environment: macOS, Python 3.11, Node 22. Z.AI API mode.",
        "codex-node-1": "Environment: Ubuntu 24.04, Python 3.12, Node 22. Direct Anthropic API.",
        "glm-node-2": "Environment: Ubuntu 24.04, Python 3.12, Node 22. Direct Anthropic API.",
    }

    return configs.get(node_name, "")
```

**大小**: ~100 bytes, ~30 token

### 总 token 预算

```
层 1: Project CLAUDE.md     ~1000 token
层 2: claude-mem 记忆        ~500 token
层 3: 智能 SHARED_CONTEXT   ~1000 token (原来 5000)
层 4: 兄弟任务状态           ~200 token
层 5: 环境配置               ~30 token
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: ~2730 token (原来 5300+)

省了 ~48%, 但信息量更大 (有记忆 + 兄弟状态)
```

---

## 三、Codex 的特殊待遇

Codex 不是普通 worker。它需要更多上下文, 因为它做的是需要判断力的任务。

### Codex Context Pack (加强版)

```python
def build_codex_context(project, task_id, spec_content):
    """Codex 的上下文包, 比 GLM 更丰富"""

    context = build_enriched_spec(project, task_id, spec_content)  # 基础

    # 额外: 完整架构决策历史
    arch_decisions = search_claude_mem(project, "architecture decision", limit=20)
    context += f"\n\n## Architecture Decision History\n{arch_decisions}"

    # 额外: 之前的失败和教训
    lessons = search_claude_mem(project, "bugfix lesson failure", limit=10)
    context += f"\n\n## Known Pitfalls\n{lessons}"

    # 额外: 项目文件树 (帮助理解全局)
    file_tree = generate_file_tree(project, max_depth=3)
    context += f"\n\n## Project File Structure\n{file_tree}"

    return context
```

### Codex 的 dispatch 方式不同

```python
def dispatch_to_codex(project, task_id, enriched_spec):
    """Codex 通过 codex exec 执行, 不是 claude -p"""

    cmd = [
        'codex', 'exec',
        '--skip-git-repo-check',
        '--full-auto',
        '-C', str(Path.home() / 'Downloads' / project),
        enriched_spec,
        '--json'
    ]

    # Codex 在 Mac-1 本地执行 (不是远程)
    subprocess.Popen(cmd, ...)
```

Codex 优势:
- 在 Mac-1 本地执行, 可以直接读 claude-mem、specs、代码库
- 有 codex session 记忆 (可以 resume)
- 可以操作 Chrome CDP (浏览器自动化)
- 比 GLM 强的推理能力

---

## 四、密钥同步 (最小方案)

不把密钥同步到 GCP。让 task-wrapper.sh 自己从环境变量读。

```bash
# Mac-2: ZAI_API_KEY 已在 .bashrc 里
# GCP: 如果需要, 在 dispatch.py 里 SSH 设置一次
```

对于 GCP 节点用 direct API (Anthropic), 不需要 Z.AI 密钥。
对于 Mac-2 用 zai API, Z.AI 密钥已在 Mac-2 环境变量里。

**原则**: 密钥不跨网络传输。每个节点用自己的 API 通道。

---

## 五、实现整合到 dispatch.py

### 修改点

1. **dispatch.py** 增加 `build_enriched_spec()` 函数
   - 在 `deploy_task_to_node()` 之前调用
   - 生成 enriched spec → 写到 `tasks/<id>/spec.md`
   - 原始 spec 保存为 `tasks/<id>/spec_original.md`

2. **dispatch.py** 增加 `dispatch_codex()` 函数
   - 对 integration/verification/fix 类型的任务
   - 调用 `codex exec` 而不是 SSH claude -p
   - 注入加强版上下文

3. **dispatch.py** 增加 `task_type_router()` 函数
   ```python
   def get_task_type(task_id):
       if task_id.startswith('S'):
           return 'implementation'  # → GLM
       elif task_id.startswith('V'):
           return 'verification'   # → Codex
       elif task_id.startswith('F'):
           return 'fix'            # → Codex
       elif task_id == 'S99':
           return 'integration'    # → Codex
       else:
           return 'implementation' # → GLM default
   ```

4. **nodes.json** 增加 Codex 节点
   ```json
   {
     "name": "codex-local",
     "host": "localhost",
     "ssh_cmd": null,
     "slots": 3,
     "api_mode": "codex",
     "executor": "codex"
   }
   ```

---

## 六、完整工作流 (20 分钟闪电战 V3)

```
T+0    Howard: "做 <project>"
T+0    Opus: 确认 specs 就绪 (≤1 轮)
T+1    Opus: python3 dispatch.py start <project>
       Controller 自动:
         1. 扫描 S*.md specs
         2. 为每个 spec 注入上下文 (claude-mem + CLAUDE.md + 智能 SHARED_CONTEXT + 兄弟状态)
         3. 按任务类型路由:
            - S01-S18 → GLM 并行 (23 slots, enriched spec)
            - S99 → 等 S* 完成后 Codex 执行 (integration)
         4. SCP enriched spec 到各节点
         5. SSH 启动 task-wrapper.sh
T+12   GLM 完成 18/18
T+13   Controller 自动触发 Phase B: 收集产物
T+14   Controller 生成 S99-integration spec → Codex 执行
T+16   Codex 完成集成
T+17   Controller 生成 V01-verify spec → Codex 执行
T+18   Codex 发现问题 → 生成 F01-fix → Codex 执行
T+19   V02 验证通过
T+20   Controller 生成 report.md
T+20   Opus: 读 report → PASS (≤1 轮)

Opus 总共: 3 轮。每个 worker 都有上下文。
```

---

## 七、实施者

| 组件 | 执行者 | 原因 |
|------|--------|------|
| build_enriched_spec() | **Codex** | 需要理解 claude-mem schema + 智能提取 |
| task_type_router() | **Codex** | 需要理解 dispatch 全局逻辑 |
| dispatch_codex() 集成 | **Codex** | Codex 自己知道怎么调用自己 |
| feedback loop (Phase B-G) | **Codex** | 跨文件推理 + 验证逻辑 |
| task-wrapper.sh 微调 | GLM | 简单 bash 修改 |
| 端到端测试 | **Codex** | 需要 SSH + 多节点 + 判断力 |
