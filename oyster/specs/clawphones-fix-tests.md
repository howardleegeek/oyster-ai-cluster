## 任务: 修复 ClawPhones 后端测试套件

### 背景
pytest 跑出 3 FAILED + 19 ERROR。安全测试 (4个) 全绿，问题在测试代码本身。

### 仓库
`~/.openclaw/workspace/proxy/`

### 问题 1: 14 个 async test ERROR (pytest-asyncio 配置)
**文件**: `test_api.py`
**原因**: `@pytest.mark.asyncio` 标记的测试报 `PytestRemovedIn9Warning`，async 函数没被正确执行
**修复**: 在 `proxy/` 目录下创建 `conftest.py` 或 `pytest.ini`，加上:
```ini
[pytest]
asyncio_mode = auto
```

### 问题 2: 5 个 import path ERROR
**文件**: `tests/test_upload_and_chat_files.py`
**原因**: `import proxy.server as server` 失败，因为从 `proxy/` 目录跑 pytest 时 `proxy` 不是一个 package
**修复**: 改成 `import server` (和 `test_file_upload_and_chat.py` 一样的方式)
- 第 19 行: `import proxy.server as server` → `import server`

### 问题 3: test_health FAILED
**文件**: `test_api.py` 约第 88 行
**原因**: 期望 `data.get("ok") is True` 但 server 返回 `{"status": "ok", "env": "DEV", "routes_loaded": [...]}`
**修复**: 改断言匹配实际响应:
```python
assert data.get("status") == "ok"
```

### 问题 4: test_upload 2 个 FAILED
**文件**: `tests/test_file_upload_and_chat.py` 约第 66 行和第 131 行
**原因**: 期望 `payload["filename"]` 但上传 response 没有 `filename` key
**修复**: 读 `server.py` 里 POST /v1/upload 端点的实际返回格式，按实际 response key 修改断言。可能是 `file_id` 或 `name` 或其他 key。

### 步骤
1. 读 server.py 找 POST /v1/upload 端点的 response 格式
2. 读 server.py 找 GET /health 端点的 response 格式
3. 创建 proxy/pytest.ini 设置 asyncio_mode = auto
4. 修 tests/test_upload_and_chat_files.py 的 import path
5. 修 test_api.py test_health 的断言
6. 修 tests/test_file_upload_and_chat.py 的 upload 断言
7. 跑 pytest 验证全绿

### 验收标准
- [ ] `MOCK_MODE=1 ADMIN_KEY=test python3 -m pytest test_api.py tests/ -v --tb=short` 全 PASS 或 ERROR 数降到 0
