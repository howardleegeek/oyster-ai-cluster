---
task_id: S01-007
project: clawphones
priority: 1
depends_on: ["S01-006"]
modifies: ["proxy/e2e/frontend.spec.ts"]
executor: glm
---

## 目标
前端浏览器测试：文件上传与网络错误处理

## 约束
- Playwright 端到端测试
- 验证错误场景

## 具体改动
- 完善 proxy/e2e/frontend.spec.ts
  - 文件上传功能测试
  - 网络错误提示测试
  - 超时处理测试

## 验收标准
- [ ] 文件上传测试通过
- [ ] 错误处理测试通过
