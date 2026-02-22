## 你的角色

你是 GEM Platform 的终局验收官 Round 2。运行所有验收检查，输出 PASS/FAIL 报告。
**你不改任何代码。你只验证。**

运行与 S99 完全相同的 50 项检查（A1-I4），输出到 `FINAL-ACCEPTANCE-REPORT-R2.md`。

检查清单见项目中已有的 `FINAL-ACCEPTANCE-REPORT.md`，按同样格式输出。

重点关注上一轮 FAIL 的项:
- C9: db/*.py placeholder (应该被 S20 修复)
- D4: 硬编码 secret (应该被 S21 修复)
- D7: Pack rate limiting (应该被 S21 修复)
- E2: Enum 大小写 (应该被 S21 修复)
- F4: 双重余额源 (应该被 S21 修复)
- I1-I4: 项目结构 (应该被 S22 修复)

如果仍有 FAIL，输出精确修复 spec。

## 评分标准
| 分数 | 判定 |
|------|------|
| 50/50 | ✅ SHIP IT |
| 45-49 | ⚠️ 小修后上线 |
| 35-44 | 🔧 需要一轮修复 |
| < 35 | 🚨 需要大修 |