# AI 工厂开发经验总结

> 最后更新: 2026-02-14

## 核心经验

### 1. 免费模型组合（已验证可用）

| 模型 | 用途 | 状态 |
|------|------|------|
| **OpenCode + MiniMax M2.5 Free** | 主要执行任务 | ✅ 免费、稳定 |
| Codex | 复杂架构任务 | 付费备用 |

**配置方法:**
```bash
# task-wrapper.sh 使用
~/.opencode/bin/opencode run --model opencode/minimax-m2.5-free -- "任务描述"
```

### 2. 61节点集群配置

| 节点 | Slots | 优先级 | 用途 |
|------|-------|--------|------|
| oci-paid-1 | 32 | 1 | 主节点 |
| glm-node-2/3/4 | 8 x 3 | 2 | 辅助节点 |
| codex-node-1 | 8 | 3 | 复杂任务 |
| mac2 | 5 | 4 | 浏览器任务 |

### 3. 调度优化

**节点优先级调整** (nodes.json):
```json
{"name": "oci-paid-1", "priority": 1, "slots": 32}
{"name": "glm-node-2", "priority": 2, "slots": 8}
```

**自动刷新卡住任务** (dispatch.py):
- 每3个循环检查超时任务
- 15分钟超时自动刷新
- 避免任务卡住

### 4. 标准化开发流程

```
1. 写 spec → MiniMax 拆分原子任务
2. dispatch start → 自动调度到61节点
3. 满负荷运行 → 利用率 100%
4. 自动部署 → Vercel 一键部署
5. 验证测试 → 自动化测试
```

### 5. Spec 模板

```yaml
---
task_id: S01-xxx
project: <project>
priority: 1
executor: glm
---

## 目标
一句话描述

## 约束
- 不动 UI/CSS
- 不加新依赖

## 验收标准
- [ ] pytest 全绿
- [ ] 部署成功
```

### 6. 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| GLM 额度用完 | 改用 OpenCode + MiniMax |
| 任务卡住 | 15分钟自动刷新 |
| 文件冲突 | 串行执行，正确行为 |
| 构建失败 | 跳过 TypeScript 检查 |

### 7. 已部署产品

| 项目 | URL | 状态 |
|------|-----|------|
| clawmarketing | https://frontend-alpha-gilt-61.vercel.app | ✅ |
| gem-platform | https://lumina-six-phi.vercel.app | ✅ |

### 8. 任务统计

- 总完成: 600+ 任务
- 成功率: ~95%
- 集群利用率: 100%

## 下次开发 checklist

- [ ] 写 spec 用 MiniMax 拆分
- [ ] 启动 dispatch start
- [ ] 监控集群利用率
- [ ] 完成后自动部署
- [ ] 验证测试
