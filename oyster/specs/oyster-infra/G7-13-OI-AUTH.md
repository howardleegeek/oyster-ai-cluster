---
task_id: G7-13-OI-AUTH
project: oyster-infra
priority: 1
depends_on: []
modifies: ["src/auth/shared.py", "src/middleware/project_auth.py"]
executor: glm
---
## 目标
统一跨项目身份认证与授权

## 技术方案
1. 新增 `SharedAuthService`，支持 JWT + API Key 两种模式
2. 项目级权限矩阵：CM, GP, BP, CV, CP, OI 各自权限
3. 中间件验证所有跨项目 API 调用
4. 审计日志记录跨项目访问

## 约束
- 不影响现有项目内部认证
- 基础测试覆盖权限校验
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] 认证延迟 < 50ms
- [ ] 支持 6 个项目权限配置
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
