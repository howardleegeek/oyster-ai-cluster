## 任务: GEM 后端代码交叉验证

### 背景
GEM RWA 平台后端 (FastAPI) 经过 GLM 集群并发生成 + import fix，需要全面验证代码质量。
两个 GCP 节点独立检查，交叉对比结果。

### 代码位置
`~/Downloads/gem-platform/backend/app/` — 95 个 Python 文件

### 检查清单

#### 轮1: 基础完整性 (codex-node-1 负责)
1. **语法检查**: 所有 .py 文件 `python -c "import ast; ast.parse(open('file').read())"` 通过
2. **Import 链完整**: `python -c "from app.app import app; print(len(app.routes))"` 能加载所有 router
3. **依赖完整**: requirements.txt 包含所有 import 的第三方包 (pydantic_settings, fastapi, sqlalchemy, redis 等)
4. **模型一致性**: models/ 里的字段和 schemas/ 里的字段对应
5. **Router 注册**: app.py include_router 的数量 = api/ 目录下 router 文件数量
6. **Enum 完整**: enums.py 里定义的 enum 覆盖所有 models/ 和 schemas/ 引用的 enum
7. **__init__.py 导出**: 所有 db/services/models/schemas 的 __init__.py 导出与实际文件匹配

#### 轮2: 代码质量 (glm-node-2 负责)
1. **API 设计一致性**: 所有 endpoint 命名风格统一 (snake_case path, RESTful)
2. **错误处理**: 每个 service 方法有 try/except 或用 error.py 的异常类
3. **依赖注入**: FastAPI Depends() 参数顺序正确 (Depends 在前, 有默认值的在后)
4. **SQL 注入防护**: 所有 DB 查询用 SQLAlchemy ORM/参数化, 无 raw SQL 拼接
5. **类型标注**: 所有 API endpoint 有返回类型标注
6. **重复代码**: 检查 services/ 之间是否有复制粘贴的重复逻辑
7. **循环 import**: 检查是否有 A→B→A 的循环引用
8. **硬编码**: 无硬编码密钥/URL/端口 (应通过 config.py 读取)

### 输出格式
每个节点输出一份 verification report:
```
## GEM Backend Verification Report — [节点名]
### PASS
- [x] 检查项: 说明
### FAIL
- [ ] 检查项: 问题描述 + 文件:行号 + 建议修复
### WARN
- [⚠️] 检查项: 潜在问题
### 统计
- 总检查项: X
- PASS: X
- FAIL: X
- WARN: X
```
