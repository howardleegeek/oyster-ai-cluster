---
task_id: S27-error-handling
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
添加全局错误处理和异常管理

##具体改动
1. 创建 backend/middleware/exception_handler.py - 全局异常处理
2. 创建 backend/schemas/error.py - 统一错误响应格式
3. 修改 main.py 注册异常处理器
4. 添加详细日志记录

##验收标准
- [ ] 所有API错误返回统一格式
- [ ] 异常有详细日志
- [ ] 500错误不泄露敏感信息
