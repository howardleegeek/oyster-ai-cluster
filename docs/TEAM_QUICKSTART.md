# 团队快速入门

> 5 分钟上手 Oyster Labs AI 集群

## 你会拿到什么

Howard 会给你：
1. **SSH 私钥文件** — 类似 `leo-oyster` 或 `kaichen-oyster`
2. **密码** — 口头告诉你

## Step 1: 配置 SSH

```bash
# 把私钥放到正确位置
mv ~/Downloads/<your-key> ~/.ssh/<your-key>
chmod 600 ~/.ssh/<your-key>

# 测试登录
ssh -i ~/.ssh/<your-key> <your-user>@34.145.79.154
```

| 成员 | 用户名 | 私钥文件 |
|------|--------|----------|
| Leo | `leo` | `leo-oyster` |
| Kai Chen | `kaichen` | `kaichen-oyster` |

登录命令示例：
```bash
# Leo
ssh -i ~/.ssh/leo-oyster leo@34.145.79.154

# Kai Chen
ssh -i ~/.ssh/kaichen-oyster kaichen@34.145.79.154
```

## Step 2: 熟悉环境

登录后你在 **glm-node-2**（网关节点），目录结构：

```
~/
├── dispatch/          # 调度系统
│   ├── dispatch.py    # 主调度器
│   ├── nodes.json     # 节点配置 (7 节点, 140 slots)
│   └── dispatch.db    # 任务数据库 (自动生成)
├── specs/             # 你的 spec 文件放这里
│   └── <project>/
│       ├── S01-xxx.md
│       └── S02-yyy.md
└── projects/          # 项目代码 (如果需要同步到节点)
    └── <project>/
```

## Step 3: 写 Spec

Spec 就是任务描述文件，dispatch 读取后自动分发到节点执行。

```bash
# 创建项目 spec 目录
mkdir -p ~/specs/my-project

# 写第一个 spec
vi ~/specs/my-project/S01-hello-world.md
```

### Spec 模板

```yaml
---
task_id: S01-hello-world
project: my-project
priority: 1
depends_on: []
modifies: ["src/main.py"]
executor: glm
---

## 目标
实现 hello world 功能

## 约束
- 不动 UI/CSS
- 不引入新依赖

## 具体改动
- `src/main.py`: 添加 hello_world() 函数

## 验收标准
- [ ] python3 -c "from src.main import hello_world; hello_world()" 输出 "Hello World"

## 不要做
- 不改其他文件
- 不加 TODO/FIXME
```

### Spec 命名规则

| 前缀 | 含义 |
|------|------|
| `S01-` | 第一个 spec (S = Spec) |
| `S02-` | 第二个，以此类推 |
| `P01-` | 并行 spec (P = Parallel) |

### 关键字段

| 字段 | 说明 |
|------|------|
| `task_id` | 唯一标识，和文件名一致 |
| `project` | 项目名 |
| `priority` | 1=最高, 2=普通, 3=低 |
| `depends_on` | 依赖的其他 spec ID (如 `["S01-setup"]`) |
| `modifies` | 会修改的文件路径 (用于文件锁，防冲突) |
| `executor` | `glm` (默认) 或 `codex` |

## Step 4: 运行任务

```bash
# 启动调度 (会阻塞，按 Ctrl+C 停止)
dispatch start my-project

# 或后台运行
dispatch start my-project --daemon

# 查看状态
dispatch status my-project

# 查看所有项目状态
dispatch status

# 生成报告
dispatch report my-project

# 停止
dispatch stop my-project
```

### 输出示例

```
=== Task Status ===
  completed: 3
  running: 2
  pending: 1

=== Node Status ===
  codex-node-1: 2/8 slots used [✓]
  glm-node-2: 1/8 slots used [✓]
  glm-node-3: 0/8 slots used [✓]
  glm-node-4: 0/8 slots used [✓]
  oci-paid-1: 5/40 slots used [✓]
  oci-paid-3: 3/48 slots used [✓]
  oci-arm-1: 0/20 slots used [✓]

=== Running Tasks ===
  S01-hello-world on oci-paid-1 (running 45s)
  S02-add-tests on codex-node-1 (running 12s)
```

## Step 5: 多 Spec 并行 + 依赖

```
S01-setup (先跑)
  ├── S02-feature-a (S01 完成后并行)
  ├── S03-feature-b (S01 完成后并行)
  └── S04-integrate (等 S02 + S03 都完成)
```

对应的 spec `depends_on`:
```yaml
# S01: depends_on: []
# S02: depends_on: ["S01-setup"]
# S03: depends_on: ["S01-setup"]  
# S04: depends_on: ["S02-feature-a", "S03-feature-b"]
```

## 可用节点

| 节点 | 类型 | Slots | 说明 |
|------|------|-------|------|
| codex-node-1 | GCP | 8 | |
| glm-node-2 | GCP | 8 | 网关节点 (你登录的地方) |
| glm-node-3 | GCP | 8 | |
| glm-node-4 | GCP | 8 | |
| oci-paid-1 | Oracle | 40 | 16核 47G 大节点 |
| oci-paid-3 | Oracle | 48 | 16核 54G 大节点 |
| oci-arm-1 | Oracle ARM | 20 | ARM 架构 |
| **总计** | | **140** | |

## 常见问题

### Q: spec 写错了怎么办？
修改 spec 文件，重新 `dispatch start`。dispatch 会跳过已完成的任务，只跑新的或修改过的。

### Q: 任务卡住了？
```bash
dispatch status my-project   # 看 running 多久了
dispatch stop my-project     # 停掉重来
```

### Q: 怎么看任务日志？
任务日志在远程节点 `~/dispatch/<project>/tasks/<task-id>/` 下。

### Q: 我和别人的任务会冲突吗？
不会。每个用户有独立的 `~/dispatch/`, `~/specs/`, `~/projects/`，独立的数据库。节点资源（slots）是共享的，先到先得。

### Q: 如何上传项目代码？
```bash
# 在本地
scp -i ~/.ssh/<your-key> -r ./my-project <your-user>@34.145.79.154:~/projects/my-project
```

---

**有问题找 Howard 或开 Issue!**
