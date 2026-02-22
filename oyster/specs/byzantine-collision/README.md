# 拜占庭对撞器 (Byzantine Collider)

> AI-to-AI 产品碰撞系统 — 用集群算力对撞出想法

## 快速开始

```bash
# 发起一次对撞
python3 ~/Downloads/dispatch/dispatch.py start byzantine-collision
```

## 概念

- **对撞主题**：需要碰撞的产品/商业问题
- **挑战者 (Challenger)**：专门质疑、挑毛病、找风险
- **辩护者 (Defender)**：为方案辩护，提供证据反驳
- **轮次**：一来一回为一轮，默认 3 轮
- **观察者 (Observer)**：记录碰撞火花，最终总结

## 使用场景

1. **需求访谈** — AI 模拟用户、PM、投资人提问
2. **竞品分析** — 两个 AI 分别扮演不同竞品，互相攻击
3. **商业化论证** — 挑战者质疑商业假设，辩护者反驳
4. **PMF 验证** — 质疑-验证-迭代，快速验证想法

## 模板文件

| 文件 | 角色 |
|------|------|
| `BYZ-XXX-challenger.md` | 挑战者 prompt |
| `BYZ-XXX-defender.md` | 辩护者 prompt |
| `BYZ-XXX-observer.md` | 观察者总结 |

## 调度方式

```bash
# 启动对撞（挑战者先手）
python3 ~/Downloads/dispatch/dispatch.py start byzantine-collision

# 收集结果
python3 ~/Downloads/dispatch/dispatch.py collect byzantine-collision

# 生成报告
python3 ~/Downloads/dispatch/dispatch.py report byzantine-collision
```

## 下一步

- [ ] 支持多轮对撞自动流转
- [ ] 支持网络调研模式（AI 搜索+分析）
- [ ] 支持人机混合模式（AI + 真人）
- [ ] 输出结构化 JSON 报告
