---
task_id: S01-006
project: clawphones
priority: 1
depends_on: []
modifies: ["proxy/e2e/frontend.spec.ts"]
executor: glm
---

## 目标
前端浏览器测试：Playwright 基础功能测试

## 约束
- 使用 Playwright
- 覆盖 Web 前端（如有）

## 具体改动
- 创建 proxy/e2e/frontend.spec.ts
  - 登录/注册页面测试
  - 会话列表页面测试
  - 聊天页面功能测试

## 验收标准
- [ ] Playwright 测试通过
- [ ] 页面加载无 JS 错误
