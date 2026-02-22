---
task_id: S06-QUALITY-GATE-TELOS
project: clawmarketing
priority: 1
depends_on: [S01-LLM-ROUTER]
modifies:
  - backend/agents/quality_gate.py
executor: glm
---

## 目标
升级 QualityGate 为 TELOS-aware 验证

## 具体改动
1. 修改 QualityGate.check() 接受 brand_telos 参数
2. Pass 1: 结构检查 (长度、大小写) - 无需 LLM
3. Pass 2: 语义检查:
   - 检查 taboo 词
   - 用 LLM 检查 tone 匹配度
4. 返回结构: {score: float, issues: list, passed: bool}
5. 通过标准: score >= 0.7

## 验收标准
- [ ] 包含 taboo 词的内容被拒绝
- [ ] tone 不匹配的内容被降分
- [ ] 通过的内容 score >= 0.7
- [ ] black backend/agents/quality_gate.py 检查通过

## 不要做
- 不动其他文件
