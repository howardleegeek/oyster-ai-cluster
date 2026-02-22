---
task_id: S01-xxx
project: <project>
priority: 1
depends_on: []
modifies:
  - path/to/file1
  - path/to/file2
executor: glm
---

## 目标
[一句话：用户可感知的结果 / 业务目标]

## 约束
- [边界：不动哪些模块/不改 UI/CSS/不加新依赖/不做重构...]
- [安全：不硬编码 secret；不提交 .env；不泄露内部错误]

## 工作包边界 (Work Pack)
- [把强耦合且必须串行的内容放在同一个 spec，避免拆成一串小任务造成固定开销]
- [把真正可并行的内容按模块/文件边界拆开；尽量不要让多个 spec 修改同一文件]

## 具体改动
- `path/to/file1`: [改动点 1 / 关键逻辑]
- `path/to/file2`: [改动点 2 / 关键逻辑]

## 验收标准
- [ ] [功能验收条件 1]
- [ ] [功能验收条件 2]
- [ ] 验证命令（必须可退出、非 watch、尽量 targeted、必要时加硬超时）
  - 后端示例: `timeout 20m pytest -q tests/test_xxx.py`
  - 前端示例: `timeout 20m npm test -- --run path/to/xxx.test.tsx`
  - 全量(仅最终集成/收口 spec): `./run.sh test` / `make test`

## 依赖策略
- `depends_on` 只写“硬依赖”（缺了就无法实现/无法编译/无法测试）。
- “软依赖”（只需要接口/类型/契约）不要写进 `depends_on`：先补最小契约（类型/API/JSON 示例），实现 spec 并行推进，最后用 wiring/integration spec 收口。

## 不要做
- [不碰的文件/模块]
- [禁止 TODO/FIXME/placeholder 交付；必须通过验收命令再宣称完成]
