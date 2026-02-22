# GEM Backend Comparison: gema-backend-main vs gem-platform/backend

## 任务
深度对比两个后端代码库，产出详细对比报告。CTO 说 gema-backend-main 才是正式后端。

## 两个代码库
1. **gema-backend-main** (CTO 认可): `~/Downloads/gema-backend-main/app/`
2. **gem-platform/backend** (我们 Sprint 1 做的): `~/Downloads/gem-platform/backend/app/`

## 对比维度（每个维度都要列具体文件+行数+代码片段）

### 1. 架构对比
- 目录结构差异
- 入口 app.py 对比 (middleware, CORS, router mount)
- config.py 对比 (env vars, DB config)
- 依赖对比 (requirements.txt / imports)

### 2. 数据模型对比
- models/ 下所有表对比 (表名、字段、类型、关系)
- 列出各自独有的表
- 列出同名表的字段差异
- DB migration 方式

### 3. API 端点对比
- 列出两边所有端点 (method + path + 功能)
- 标注: 双方都有 / A独有 / B独有
- 对同名端点对比请求/响应 schema

### 4. Auth 系统对比
- 认证方式 (wallet, email, twitter, JWT)
- Token 管理 (生成、刷新、过期)
- 权限控制 (admin/user role)
- Rate limiting

### 5. 业务逻辑对比
- 盲盒/抽卡/lottery 系统
- NFT mint/transfer
- 支付 (SOL/USDC)
- 物流 shipping
- 推荐 referral
- 回购 buyback
- Marketplace

### 6. 外部服务对比
- Solana (web3, pytoniq, etc)
- Redis 用法
- 邮件 (SendGrid)
- Twitter OAuth
- 其他第三方

### 7. 代码质量对比
- 已知 bugs/typos (gema-backend-main 已发现: ogger.info, module_validate, prodabilities, undefined twitter_id)
- 错误处理模式
- 日志
- 测试覆盖

### 8. 合并建议
基于对比结果，给出:
- 哪些模块用 gema-backend-main 的
- 哪些模块用 gem-platform/backend 的
- 合并冲突点
- 推荐合并策略 (以谁为基础)
- 预估工作量

## 产出
写到 `~/Downloads/specs/gem-backend-comparison-report.md`，Markdown 表格为主，清晰可读。

## 注意
- 不改任何代码，只读 + 分析
- 不需要运行任何服务
- 重点是帮 Howard 做合并决策
