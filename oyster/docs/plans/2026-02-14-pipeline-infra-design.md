# Pipeline Infra Design — 2026-02-14

## 概述
独立 Python CLI 程序，管理项目从分析到部署的六层自动化流程。
调用 dispatch.py 作为黑盒（subprocess），不修改 dispatch 任何代码。

## 架构
```
pipeline.py (CLI) → Layer 状态机 → Executor 调用
     ↓                   ↓              ↓
pipeline.db          L1-L6 层       opencode / dispatch / local
     ↓                   ↓              ↓
  runs/results        报告 JSON      集群节点执行
```

## 文件结构
```
dispatch/pipeline/
├── pipeline.py          # CLI 入口 + 状态机
├── db.py                # SQLite 管理
├── config.py            # 项目配置加载
├── projects.yaml        # 5 个项目定义
├── layers/
│   ├── __init__.py
│   ├── base.py          # Layer 基类 + LayerResult
│   ├── L1_analyze.py    # 扫描 → gap-report
│   ├── L2_implement.py  # gap → specs → dispatch
│   ├── L3_build.py      # 依赖 + 编译 + 启动
│   ├── L4_test.py       # API curl + 页面测试
│   ├── L5_fix.py        # bug → 修复 spec → dispatch
│   └── L6_deploy.py     # 部署配置生成
├── executors/
│   ├── __init__.py
│   ├── base.py          # Executor 基类
│   ├── opencode.py      # opencode run / MiniMax API
│   ├── dispatch_exec.py # subprocess 调 dispatch.py
│   └── local.py         # 本地 shell 命令
└── reports/<project>/   # JSON 报告
```

## 状态机
L1→L2→L3→L4→L5→L4(重测)→L6→DONE
失败3次→FAILED，等人工

## 关键决策
- DB: pipeline.db 独立于 dispatch.db
- dispatch: 只通过 subprocess 调用，遵守冻结令
- LLM: opencode run (MiniMax M2.5 免费)
- 浏览器测试: Mac-2 Playwright
- 报告: JSON 格式，层间可消费
