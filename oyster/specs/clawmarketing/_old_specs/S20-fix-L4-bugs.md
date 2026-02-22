---
task_id: S20-fix-L4-bugs
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
Fix the 17 S2 bugs causing L4 API tests to fail - schema mismatches between L4 test expectations and actual API responses.

## 约束
- Only fix API response schema mismatches
- Do NOT change API functionality, only fix response format
- Do NOT touch frontend code
- Do NOT add new features

## 具体改动
1. Run L4 tests and capture exact failure messages
2. Compare L4 test expected schemas with actual API response schemas
3. Fix each of the 17 bugs by aligning API responses to match expected schemas
4. Common issues to check:
   - Response field names (camelCase vs snake_case)
   - Missing required fields
   - Extra fields in response
   - Type mismatches (string vs number, etc.)
   - Nested object structure differences

## 验收标准
- [ ] Run `python3 pipeline/run.py clawmarketing L4` 
- [ ] All 17 S2 bugs fixed
- [ ] L4 tests pass

## 不要做
- Don't change API functionality
- Don't modify frontend
- Don't add new endpoints
