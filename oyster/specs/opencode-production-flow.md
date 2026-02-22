# OpenCode 自治生产流程 — Master Prompt

> 用法: `opencode run "$(cat specs/opencode-production-flow.md)" `
> 或拆成 6 步分别执行

---

## Master Prompt (一次性给 OpenCode)

```
你是一个全栈工程师。你的任务是把项目从当前状态推进到【可上线、用户可用】的生产级别。

你必须严格按照以下六层流程执行，每层完成后输出状态报告，失败则回退修复。

===== L1: 分析层 (ANALYZE) =====

目标: 搞清楚项目现状和差距

1. 读 README.md / CLAUDE.md / package.json / requirements.txt
2. 列出所有路由/页面/API endpoint
3. 找到所有 TODO / placeholder / mock / hardcoded
4. 生成差距报告:
   - 哪些功能是真的（有实际逻辑）
   - 哪些功能是假的（placeholder/mock）
   - 缺什么才能上线

输出格式:
```
## L1 分析报告
- 真实功能: [列表]
- Placeholder: [列表，含文件路径和行号]
- 上线缺失: [列表，按优先级排序]
- 预估工作量: [S/M/L 每项]
```

===== L2: 实现层 (BUILD) =====

目标: 把 placeholder 全部替换为真实实现

规则:
- 一次只改一个模块，改完立刻验证
- 不要重构已有的可工作代码
- 不要改 UI/CSS/样式（除非功能不可用）
- 每个改动必须有对应的验证方法
- 用 kwargs 不用位置参数
- 环境变量用 .env.example 记录，不硬编码

执行顺序:
1. 先修 backend（API 必须返回真实数据）
2. 再修 frontend（对接真实 API）
3. 最后修配置（环境变量、数据库连接）

每改完一个模块:
```
## L2 模块完成: [模块名]
- 改了什么: [文件列表]
- 验证命令: [具体命令]
- 验证结果: PASS/FAIL
```

===== L3: 构建层 (COMPILE) =====

目标: 确保项目能编译、能启动

1. 安装依赖:
   - Python: `pip install -r requirements.txt`
   - Node: `npm install`
2. 编译检查:
   - Python: `python -m py_compile` 对每个 .py 文件
   - TypeScript: `npx tsc --noEmit`
   - ESLint: `npx eslint src/`
3. 启动测试:
   - Backend: 启动服务，curl 检查 health endpoint
   - Frontend: `npm run build` 确认无报错
4. 数据库: 确认 migration 能跑通

输出:
```
## L3 构建报告
- 依赖安装: PASS/FAIL [详情]
- 编译检查: PASS/FAIL [错误数]
- 启动测试: PASS/FAIL [截图/日志]
- 数据库: PASS/FAIL
```

如果 FAIL → 修复后重新执行 L3，最多 3 次

===== L4: 自测层 (TEST) — 核心 =====

目标: 像用户一样测试每个功能

### 4A: API 测试（后端）

对每个 API endpoint 执行:
```bash
# 1. 正常请求
curl -X POST http://localhost:8000/api/xxx -H "Content-Type: application/json" -d '{"valid": "data"}'
# 验证: 状态码 200, 返回格式正确

# 2. 缺字段
curl -X POST http://localhost:8000/api/xxx -d '{}'
# 验证: 状态码 422, 错误信息有意义

# 3. 错误token
curl -X GET http://localhost:8000/api/xxx -H "Authorization: Bearer invalid"
# 验证: 状态码 401

# 4. 空数据库
curl -X GET http://localhost:8000/api/list
# 验证: 返回空数组，不崩溃
```

### 4B: 页面测试（前端）— 用浏览器自动化

对每个页面执行:
```
1. 导航到页面 URL
2. 等待加载完成（无 loading spinner）
3. 截图保存
4. 找到所有可点击元素（按钮、链接、输入框）
5. 逐个交互:
   - 按钮: 点击，验证响应（跳转/弹窗/数据变化）
   - 输入框: 输入测试数据，验证校验
   - 表单: 填写并提交，验证结果
   - 下拉菜单: 展开，选择，验证
6. 截图保存交互后状态
7. 检查 console 有无报错
```

### 4C: 流程测试（端到端）

测试完整用户流程:
```
流程 1: 注册 → 登录 → 进入首页 → 核心功能 → 登出
流程 2: 未登录访问受保护页面 → 应跳转到登录
流程 3: 核心业务流程（每个项目不同，见下方项目特定流程）
```

### 4D: 边界测试

```
- 空表单提交
- 超长输入（1000 字符）
- 特殊字符输入（<script>alert(1)</script>）
- 快速连续点击同一按钮
- 后端挂了前端是否有错误提示
- 刷新页面状态是否保持
```

输出:
```
## L4 自测报告
### API 测试
| Endpoint | 正常 | 缺字段 | 错token | 空数据 |
|----------|------|--------|---------|--------|
| POST /auth/login | ✅ | ✅ | ✅ | N/A |
| ... | | | | |

### 页面测试
| 页面 | 加载 | 按钮 | 表单 | Console |
|------|------|------|------|---------|
| /login | ✅ | ✅ 3/3 | ✅ | ✅ 0 errors |
| ... | | | | |

### 流程测试
| 流程 | 结果 | 问题 |
|------|------|------|
| 注册→登录→首页 | ✅ | 无 |
| ... | | |

### 发现的 Bug
1. [Bug描述] - [文件:行号] - 严重程度 S1/S2/S3
```

===== L5: 修复层 (FIX) =====

目标: 修复 L4 发现的所有 bug

规则:
- S1 (崩溃/数据丢失) 必须修
- S2 (功能异常) 必须修
- S3 (体验问题) 尽量修
- 每修一个 bug，重新跑 L4 对应的测试
- 修复不能引入新 bug（回归测试）

循环: L4 → L5 → L4 → L5 ... 最多 3 轮

输出:
```
## L5 修复报告 (Round N)
| Bug | 修复方式 | 改了什么文件 | 回归测试 |
|-----|----------|-------------|----------|
| ... | ... | ... | PASS/FAIL |
```

===== L6: 部署层 (DEPLOY) =====

目标: 生成可直接部署的配置

1. 环境变量:
   - 生成 .env.example（所有必需变量）
   - 标注哪些需要用户填写（API key 等）

2. Docker:
   - 确认 Dockerfile 能 build
   - 确认 docker-compose 能启动全栈
   - 验证容器间通信

3. 部署配置:
   - 静态站: 生成 vercel.json
   - API: 生成 fly.toml 或 railway.json
   - 数据库: 生成 migration 脚本

4. 上线检查清单:
   ```
   - [ ] HTTPS 配置
   - [ ] CORS 设置（只允许自己的域名）
   - [ ] 环境变量全部设置
   - [ ] 数据库 migration 执行
   - [ ] 静态文件 CDN
   - [ ] 错误监控（Sentry 等）
   - [ ] 日志收集
   - [ ] 健康检查 endpoint
   ```

输出:
```
## L6 部署报告
- 部署方式: [Vercel/Fly.io/Docker]
- 部署命令: [具体命令]
- 预估费用: [$/月]
- 上线 URL: [待填]
- 检查清单完成度: X/Y
```

===== 全局规则 =====

1. 每层完成必须输出报告
2. 任何层 FAIL 3 次 → 停下来，输出当前状态，等指令
3. 不要删除任何已有功能
4. 不要改动不相关的文件
5. 所有改动都能 git diff 看到
6. 敏感信息（API key）只用环境变量
```

---

## 项目特定流程（附加到 Master Prompt 后面）

### ClawMarketing 特定
```
核心业务流程:
1. 创建品牌 → 设置 persona → 生成内容 → 预览 → 发布
2. 查看分析面板 → 数据图表正确渲染
3. A/B 测试创建 → 对比结果

重点修复:
- backend/agents/ 下所有 placeholder 替换为真实 LLM 调用
- 用 MiniMax API (已有 key) 替代 _call_llm placeholder
- STP engine 用真实 prompt 替代 mock
```

### GEM Platform 特定
```
核心业务流程:
1. 注册 → 浏览盲盒 → 购买 → 开盒 → 查看结果
2. 钱包连接 → Vault 查看 → 交易历史
3. 管理员: 创建盲盒 → 设置概率 → 上架

重点修复:
- Solana 交易 placeholder → devnet 真实调用
- Stripe 支付流程端到端
- Mystery box 概率算法验证
```

### ClawPhones 特定
```
核心业务流程:
1. 打开 app → 注册 → 与 AI 对话 → 收到回复
2. 切换模型 (free/pro) → 验证不同回复质量
3. 文件上传 → AI 分析 → 返回结果

重点修复:
- Push notification (之前 FAIL)
- Production proxy 部署
- Token 刷新机制
```

### ClawVision.org 特定
```
核心业务流程:
1. 首页加载 → 地图渲染 → 数据点显示
2. API 页面 → 文档正确 → 示例可运行
3. 白皮书页面 → 内容完整

重点修复:
- localhost:8787 → 生产 API URL
- 地图数据加载优化
```

### Oysterworld 特定
```
核心业务流程:
1. 打开网页 → 授权相机/GPS → 拍照上传
2. 查看地图 → 看到自己和别人的上传
3. 任务系统 → 领取任务 → 完成 → 获得奖励

重点修复:
- 从 prototype 升级到 production 架构
- 加认证系统
- HTTPS（相机需要）
- 真实数据库替代文件存储
```

---

## 执行命令

```bash
# 方式 1: 一次性全流程（适合小项目如 ClawVision）
opencode run "$(cat specs/opencode-production-flow.md)

项目路径: ~/Downloads/clawvision-org/
执行全部 6 层。"

# 方式 2: 分层执行（适合大项目）
opencode run "读 specs/opencode-production-flow.md，对 ~/Downloads/gem-platform/ 执行 L1 分析层"
# 看报告 → 确认 → 继续
opencode run "继续 L2 实现层，按 L1 报告的优先级"
# ...逐层推进

# 方式 3: 通过 bridge 让 Opus 监控
BRIDGE_IDENTITY=opus python3 ~/Downloads/dispatch/bridge.py send opencode chat \
  '{"text":"执行 specs/opencode-production-flow.md L1-L6 对 gem-platform，每层完成发报告回来"}'
```

---

## 优先级排序（建议执行顺序）

| 顺序 | 项目 | 理由 | 预估 |
|------|------|------|------|
| 1 | ClawVision.org | 95% 完成，改个 URL 就能上线 | 1 小时 |
| 2 | GEM Platform | 78%，Vercel 部署就绪 | 1 天 |
| 3 | ClawPhones | 85%，proxy 需要部署 | 2 天 |
| 4 | ClawMarketing | 40%，AI placeholder 多 | 3-5 天 |
| 5 | Oysterworld | 20%，需要大量新代码 | 1-2 周 |
