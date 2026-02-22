# AI 工厂最佳实践 (闭环改进)

> 来源: 从一次 prompt 学习总结，2026-02-13
> 核心观点: **可验证的闭环 > 完美的计划**

---

## 核心认知升级

从「调度优先」升级到「验证闭环」——每个环节都必须有明确的输入、输出、验证标准，不给 agent 任何糊弄空间。

Dispatch 系统已有强大的**调度能力**（DAG 编排、并行分发、节点管理），但缺验证闭环，这是 ClawMarketing 58% 测试通过率的根因。

---

## 七大最佳实践

### 1. 先出计划，再写代码

```
输出顺序：执行计划 → 文件树 → 逐文件代码 → README → 验收清单 → 自评
```

**教训**: S01-S18 直接 dispatch 写代码，没有统一的执行计划。导致三节点产出合并后 79 个 test fail、接口对不上。

**借鉴**:
- 每个项目开始前，先输出一份包含以下内容的执行计划
- 里程碑拆分（至少 6 步，有先后依赖）
- 模块边界（谁写什么，不碰什么）
- 数据模型设计（统一的 schema）
- API 列表（含请求/响应示例）——SHARED_CONTEXT
- **风险清单 + 缓解策略**（我们缺这个）

---

### 2. 共享契约是铁律

```
模块边界：前端 / 后端 / 共享契约 / 测试
```

**教训**: SHARED_CONTEXT.md 写了但不够硬。PersonaEngine 构造函数参数错位、Pydantic 大小写不一致、方法不存在——全是契约没对齐。

**借鉴**:
- 共享契约必须包含：**每个接口的请求/响应 JSON 示例**，不只是类型签名
- Spec 里必须引用契约，agent 执行前先读契约
- 契约变更 = 全停，重新对齐

---

### 3. 一键启动 + 一键测试

```
./run.sh dev   启动前后端
./run.sh test  运行所有测试
```

**教训**: ClawMarketing 到现在都没有统一的启动/测试命令。每次验证都临时拼命令。

**借鉴**:
- 项目根目录必须有 `run.sh` 或 `Makefile`
- `make dev` = 启动全栈
- `make test` = 跑全部测试
- 这是 agent 自验证的基础——spec 的验收标准直接写 `./run.sh test`

---

### 4. Revision + 冲突检测

```
PATCH 必须带 baseRevision；不匹配返回 409
```

**教训**: 32 个 agent 并行改同一个项目，没有任何冲突检测。rsync basename 冲突、同文件互踩。

**借鉴**:
- 每个 spec 的 `modifies` 字段是我们的"锁"
- dispatch 应该检查：两个 running 任务的 modifies 有交集 → 串行不并行
- collect 回来时做 diff 检查，有冲突报 409 而不是静默覆盖

---

### 5. 测试不是可选的

```
后端单测 >= 12, 前端单测 >= 8, E2E >= 5
否则判定失败
```

**教训**: S01-S18 写了 19 个测试文件，但 58% 通过率，27 个 ERROR。测试是"写了但没人跑"的装饰品。

**借鉴**:
- Spec 模板强制加：`verify: ./run.sh test`
- Agent 执行完必须跑测试，测试不过 = 任务失败，不算 completed
- task-wrapper.sh 结尾加测试步骤，测试红 → status = failed

---

### 6. 导入/导出验证闭环

```
导入后再导出应保持等价（可通过测试证明）
```

**借鉴**: 应用到 dispatch 回收链——
- 代码从 Mac-1 → 节点（export）
- Agent 改完 → 回收到 Mac-1（import）
- **import 后的代码 build/test 必须通过 = 闭环验证**
- 不通过就不 merge

---

### 7. 严格输出格式

```
不要跳过任何硬约束
不要只给伪代码
不要用 TODO 糊弄
```

**教训**: GLM agent 经常输出"已完成"但实际只写了注释 `# TODO: implement`，或者报告"Already Complete"但没验证。

**借鉴**:
- Spec 加约束：`禁止 TODO/FIXME/placeholder`
- task-wrapper 加验证：grep 产出代码里有没有 TODO，有就 fail
- Agent 的"已完成"声明不可信，必须跑验证命令

---

## 立即可落地的改进清单

| 改进项 | 当前状态 | 目标状态 | 优先级 |
|--------|----------|----------|--------|
| 执行计划 | 无 | 每个项目先出计划 spec | 高 |
| 一键测试 | 无 | ClawMarketing 根目录加 Makefile | 高 |
| 测试强制 | agent 报完成即完成 | task-wrapper 强制跑测试，不过 = fail | 高 |
| TODO 检查 | 无 | task-wrapper 增加 grep TODO | 中 |
| 冲突检测 | modifies 字段不检查 | dispatch.py 检查 modifies 交集 | 中 |
| 契约强化 | SHARED_CONTEXT 只有类型 | 必须带 JSON 示例 | 中 |
| 导入验证 | collect 不验证 | collect 后自动 build+test | 低 |

---

## 落地顺序建议

1. **task-wrapper.sh 增加测试强制** — 最简单、效果最直接
2. **ClawMarketing 根目录加 Makefile** — 让验证有统一入口
3. **dispatch.py 增加冲突检测** — 避免并行任务互踩
4. **Spec 模板增加执行计划段** — 从源头规范
5. **collect 后自动 build+test** — 闭环验证

---

## 一句话总结

这篇文章的核心思路是 **"可验证的闭环"**——每一步都有明确的输入、输出、验证标准，不给 agent 任何糊弄空间。我们的 dispatch 系统有调度能力但缺验证闭环，这是 ClawMarketing 58% 测试通过率的根因。
