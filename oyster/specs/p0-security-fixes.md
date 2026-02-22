## 任务: 修复 ClawPhones 6 个 P0 安全漏洞

### 背景
Sprint 2-10 功能已完成，但安全审计发现 6 个 P0 漏洞阻塞 release。必须全部修复才能上线。

### 工作目录
`~/.openclaw/workspace/`

### 修复清单

---

#### P0-1: Admin Auth Timing Attack
**文件**: `proxy/server.py` line 3564
**问题**: `not x_admin_key` short-circuit 在 `secrets.compare_digest` 前执行，泄露 header 存在性
**修复**:
```python
def _admin_check(x_admin_key: Optional[str]) -> None:
    if not ADMIN_KEY:
        raise HTTPException(status_code=404, detail="admin disabled")
    # Always run constant-time comparison, even if key is None/empty
    provided = x_admin_key or ""
    if not secrets.compare_digest(provided, ADMIN_KEY):
        raise HTTPException(status_code=401, detail="bad admin key")
```

---

#### P0-2: Hardcoded Credentials — 全部移除
**文件和行号**:
1. `proxy/scripts/auto_fix_dispatcher.py:35` — `ADMIN_KEY = "clawphones2026"`
2. `proxy/scripts/crash_analyzer.py:33` — `ADMIN_KEY = "clawphones2026"`
3. `proxy/test_api.sh:6` — `ADMIN_KEY="clawphones2026"`
4. `android/clawphones-android/app/build.gradle:91-92` — keystore passwords

**修复**:
- 文件 1-3: 改为 `ADMIN_KEY = os.environ.get("CLAWPHONES_ADMIN_KEY", "")` (Python) 或 `ADMIN_KEY="${CLAWPHONES_ADMIN_KEY:?missing}"` (Bash)
- 文件 4: Android signing passwords 改为 `System.getenv()` 或 `gradle.properties` (gitignored) 读取:
  ```gradle
  storePassword project.findProperty('KEYSTORE_PASSWORD') ?: System.getenv('KEYSTORE_PASSWORD') ?: ''
  keyPassword project.findProperty('KEY_PASSWORD') ?: System.getenv('KEY_PASSWORD') ?: ''
  ```
- 在 `proxy/.env.example` 中添加示例变量名（不含实际值）
- 确保 `.gitignore` 包含 `.env` 和 `gradle.properties`

---

#### P0-3: Rate Limiting 扩展到关键端点
**文件**: `proxy/server.py`
**当前**: 只有 login (line ~1819) 有 rate limiting
**修复**: 实现通用 rate limiter middleware，保护以下端点:

```python
# 新增通用限速器（基于 IP + 端点）
RATE_LIMITS = {
    "auth": {"requests": 10, "window": 300},      # 注册/登录/刷新
    "chat": {"requests": 60, "window": 60},        # 聊天 completions
    "upload": {"requests": 10, "window": 60},      # 文件上传
    "admin": {"requests": 5, "window": 60},        # 管理端点
    "export": {"requests": 3, "window": 300},      # 数据导出
    "crash": {"requests": 20, "window": 60},       # crash reports
    "default": {"requests": 120, "window": 60},    # 其他
}
```

**实现方式**: 用内存 dict + sliding window (已有 `_login_attempts` 做参考)
**必须保护的端点** (按优先级):
- POST /v1/auth/register
- POST /v1/auth/apple
- POST /v1/auth/refresh
- POST /v1/chat/completions (及 deepseek/kimi/claude 变体)
- POST /v1/conversations/{id}/chat
- POST /v1/conversations/{id}/chat/stream
- POST /v1/conversations/{id}/upload
- POST /admin/* (所有 admin 端点)
- POST /v1/user/export
- DELETE /v1/user/account
- POST /v1/crash-reports

---

#### P0-4: Path Traversal 修复
**文件**: `proxy/server.py` lines 2983-2986
**问题**: `stored_path` 从 DB 直接用于 FileResponse，无边界检查
**修复**:
```python
path = str(row["stored_path"])
real_path = os.path.realpath(path)
upload_dir = os.path.realpath(UPLOAD_DIR)
if not real_path.startswith(upload_dir + os.sep):
    raise HTTPException(status_code=403, detail="access denied")
if not os.path.isfile(real_path):
    raise HTTPException(status_code=404, detail="file content missing")
return FileResponse(path=real_path, media_type=str(row["mime_type"]), filename=str(row["original_name"]))
```

---

#### P0-5: HTTPS 强制
**文件**:
- `ios/ClawPhones/Services/DeviceConfig.swift:58` — 改 `http://` → `https://`
- `android/clawphones-android/app/src/main/java/ai/clawphones/agent/chat/ClawPhonesAPI.java:48` — 改 `http://` → `https://`

**额外**:
- Android: 移除 `AndroidManifest.xml` 中的 `android:usesCleartextTraffic="true"`（如果有的话改为 false）
- iOS: 确认 Info.plist 没有 ATS 例外（App Transport Security）

---

#### P0-6: Token 安全存储
**iOS** (`ios/ClawPhones/Services/DeviceConfig.swift`):
- line 92: 移除 `UserDefaults.standard.set(token, ...)` 写入
- line 26-28: getter 改为只从 Keychain 读取（KeychainHelper 已存在，直接用）
- 迁移逻辑: 首次启动从 UserDefaults 迁移到 Keychain，迁移后删除 UserDefaults 中的 token
- CrashReporter.swift: 改为从 Keychain 读 token

**Android** (`android/.../ClawPhonesAPI.java`):
- line 216: 改用 `EncryptedSharedPreferences` (AndroidX Security):
  ```java
  SharedPreferences prefs = EncryptedSharedPreferences.create(
      "clawphones_secure_prefs",
      MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
      context,
      EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
      EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
  );
  ```
- 添加 `androidx.security:security-crypto:1.1.0-alpha06` 到 build.gradle dependencies
- 迁移逻辑: 首次启动从明文 SharedPreferences 迁移到加密版本

---

### 验收标准
- [ ] P0-1: `_admin_check` 全程 constant-time，无 short-circuit
- [ ] P0-2: `grep -r "clawphones2026"` 返回 0 结果；build.gradle 不含明文密码
- [ ] P0-3: 所有列出的端点返回 429 当超过限制；原有 login rate limit 行为不变
- [ ] P0-4: FileResponse 路径必须在 UPLOAD_DIR 下；构造 `../../etc/passwd` 测试返回 403
- [ ] P0-5: 双端 BASE_URL 使用 https://；Android 无 cleartext 权限
- [ ] P0-6: iOS token 只存 Keychain；Android token 使用 EncryptedSharedPreferences
- [ ] 所有修改编译通过（Python 语法检查 + iOS 编译检查 + Gradle 编译检查）
- [ ] 无新 hardcoded secrets 引入

### 测试要求
- [ ] pytest: rate limiter 单元测试 (超限返回 429, 窗口过期后恢复)
- [ ] pytest: path traversal 测试 (正常路径通过, 穿越路径 403)
- [ ] pytest: admin auth 测试 (空 key, 错误 key, 正确 key)

### 注意
- UPLOAD_DIR 变量需要确认实际值 — 在 server.py 顶部搜索定义
- EncryptedSharedPreferences 需要 minSdkVersion >= 23 (Android 6.0)，确认 build.gradle 的 minSdk
- 不要修改 API 行为/响应格式，只做安全加固
