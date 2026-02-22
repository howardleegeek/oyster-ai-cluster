---
task_id: S215-auto-spec-generator
project: oyster-infra
priority: 2
depends_on: []
modifies: ["dispatch/auto_spec.py"]
executor: glm
---
## 目标
实现自动 spec 生成器: 分析代码库自动生成改进 spec

## 约束
- 在 dispatch 目录内添加
- 写 pytest 测试
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_auto_spec.py 全绿
- [ ] 扫描代码库检测缺失功能
- [ ] 生成符合模板的 YAML spec
- [ ] 关联相关文件和依赖

## 不要做
- 不留 TODO/FIXME/placeholder
