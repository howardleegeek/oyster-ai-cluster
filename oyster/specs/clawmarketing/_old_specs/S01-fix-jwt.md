---
task_id: S01-fix-jwt
project: clawmarketing
priority: 1
depends_on: []
modifies: ["backend/auth.py"]
executor: codex-node-1
max_retries: 3
---

## 目标
修复 auth.py 的 jwt import 错误

## 具体改动
1. 编辑 ~/Downloads/clawmarketing/backend/auth.py
2. 第6行: `import jwt` → `from jose import jwt`
3. 文件顶部添加: `from jose.exceptions import ExpiredSignatureError, InvalidTokenError`
4. 第73行: `jwt.ExpiredSignatureError` → `ExpiredSignatureError`
5. 第78行: `jwt.InvalidTokenError` → `InvalidTokenError`
6. 验证: cd ~/Downloads/clawmarketing && PYTHONPATH=. python3 -c "from backend.auth import decode_token; print('OK')"

## 验收标准
- [ ] python3 -c "from backend.auth import decode_token" 无报错
