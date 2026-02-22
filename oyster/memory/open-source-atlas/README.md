# Oyster Open Source Atlas

> **Open-Source-First**: 任何新项目/新功能，先查 Atlas，找到开源方案再开发。
> **规则**: 没有 P2 开源扫描报告，不准写代码。

## R&D v2 流程 (P0-P6)

```
P0 需求定义 → P1 能力拆解 → P2 开源扫描(强制) → P3 评估打分 → P4 选型决策 → P5 集成改造 → P6 监控反馈
```

### P0 - 需求定义
- 项目名称 + 核心目标 + 关键能力 + 性能要求

### P1 - 能力拆解
- 把项目拆成能力模块，每个模块独立匹配开源

### P2 - 强制开源扫描 (MANDATORY)
- 每个能力模块必须回答:
  1. 是否有成熟开源?
  2. GitHub stars?
  3. 最近 6 个月活跃?
  4. License 允许商用?
  5. 有生产案例?

### P3 - 评估打分
- 成熟度 (1-10) + 社区活跃度 + 商用风险 + 集成成本

### P4 - 选型决策
- 只允许三种结果: **直接用** / **Fork 改造** / **核心差异自研**
- 不允许全栈自研

### P5 - 集成改造
- 写 Adapter + Glue Code + 监控 + 容错
- 核心价值 = 组合能力，不是重写能力

### P6 - 监控反馈
- License 风险? 上游更新? Fork 偏离度?
- Fork 偏离 > 40% → 重新评估

## 目录结构

```
open-source-atlas/
├── README.md                    # 本文件
├── capability-map.md            # 能力层 → 开源映射
├── projects/                    # 按项目的开源扫描报告
│   ├── clawmarketing.md
│   ├── clawvision.md
│   └── ...
└── templates/
    └── scan-template.md         # P2 扫描报告模板
```

## 使用方法

### 调研团队
```
1. 收到新项目需求
2. 拆成能力模块 (P1)
3. 查 capability-map.md
4. 如果没有 → 用 GitHub MCP 搜索
5. 填写 scan-template.md
6. 评估打分 (P3)
7. 选型决策 (P4)
8. 开始集成 (P5)
```

### AI Agent 自动扫描 (GitHub MCP)
```
输入: "我需要分布式任务调度 + 自愈 + 节点监控"
Agent:
  1. 拆解能力关键词
  2. GitHub MCP search_repositories
  3. 按 stars/activity/license 排序
  4. 生成比较矩阵
  5. 输出推荐
```
