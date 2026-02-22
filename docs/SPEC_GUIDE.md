# Spec 编写指南

> Spec 质量 = 代码质量。好 spec → agent 做对，烂 spec → 瞎猜。

## 完整模板

```yaml
---
task_id: S01-xxx
project: <project>
priority: 1
depends_on: []
modifies:
  - path/to/file.py
  - path/to/other.py
executor: glm
---

## 目标
[一句话描述这个任务要达成什么]

## 约束
- [技术栈约束：Python 3.10+, 不引入新依赖]
- [边界约束：不动 UI/CSS/不改 schema/不做重构]
- [安全约束：不硬编码 secret；不提交 .env]

## 具体改动
- `path/to/file.py`: [详细说明改什么，怎么改]
- `path/to/other.py`: [详细说明]

## 验收标准
- [ ] [可执行的验证命令]
- [ ] pytest tests/test_xxx.py -v 全绿
- [ ] python3 -c "from module import func; assert func() == expected"

## 不要做
- [不碰的文件/模块]
- 禁止 TODO/FIXME/placeholder 交付
- 不改其他无关代码
```

## 黄金法则

### 1. 一个 Spec 一件事
```
❌ S01-重构整个后端并添加新功能
✅ S01-添加用户注册接口
✅ S02-添加用户登录接口
```

### 2. modifies 必须填准
`modifies` 用于文件锁，防止两个并行 spec 改同一个文件。填错 = 冲突。

```yaml
# ❌ 太宽泛
modifies: ["src/"]

# ✅ 精确到文件
modifies: ["src/auth/login.py", "src/auth/register.py"]
```

### 3. 验收标准必须可执行
```yaml
# ❌ 模糊
- [ ] 功能正常工作

# ✅ 可执行
- [ ] curl http://localhost:8000/api/health 返回 {"status": "ok"}
- [ ] pytest tests/test_auth.py -v 全绿
```

### 4. "不要做" 比 "要做" 更重要
Agent 容易过度发挥。明确禁止比详细指令更有效。

```yaml
## 不要做
- 不改 database schema
- 不改前端代码
- 不加新依赖到 requirements.txt
- 不重构现有函数签名
```

### 5. 约束 UI 任务
GLM 改 UI 容易跑偏，必须加硬约束：

```yaml
## 约束
- 只改 JavaScript 逻辑，不动 CSS/样式
- 保留现有 HTML 结构，只替换 mock 数据为 API 调用
- 不改组件的 props 接口
```

## 依赖编排

### 串行
```
S01-setup → S02-implement → S03-test
```
```yaml
# S02
depends_on: ["S01-setup"]
# S03  
depends_on: ["S02-implement"]
```

### 扇出 (并行)
```
S01-setup ──→ S02-feature-a
           ├→ S03-feature-b
           └→ S04-feature-c
```
```yaml
# S02, S03, S04 各自:
depends_on: ["S01-setup"]
```

### 扇入 (汇聚)
```
S02-feature-a ──┐
S03-feature-b ──┼→ S05-integrate
S04-feature-c ──┘
```
```yaml
# S05
depends_on: ["S02-feature-a", "S03-feature-b", "S04-feature-c"]
```

## 优先级

| 值 | 含义 | 用途 |
|---|------|------|
| 1 | 最高 | 关键路径、阻塞其他任务 |
| 2 | 普通 | 默认值 |
| 3 | 低 | 优化、文档、非紧急 |

## 血泪教训

1. **Spec 写 "重构 + 新功能"** → agent 两头不讨好 → 拆成两个 spec
2. **没写 "不要做"** → agent 顺手重构了半个项目
3. **验收标准写 "功能正常"** → 无法自动验证 → 必须给命令
4. **modifies 漏了文件** → 两个 spec 同时改一个文件 → 冲突
5. **depends_on 写多了** → 假串行，浪费并行能力
6. **失败 2 次 → 换方案** → 不要盲目重试同一个 spec
