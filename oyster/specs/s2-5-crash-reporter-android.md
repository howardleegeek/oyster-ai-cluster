## 任务: Android CrashReporter (S2-5 P0)

### 背景
后端已有 POST /v1/crash-reports 端点。需要在 Android 端实现 crash 捕获 + 上报。

### 新增文件
`app/src/main/java/ai/clawphones/agent/CrashReporter.java`

### 功能要求

#### 1. 初始化 (在 Application 或 LauncherActivity 中调用)
```java
public static void init(Context context) {
    // 设置全局 UncaughtExceptionHandler
    Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
        saveCrashToFile(context, throwable, true);
        // 调用系统默认 handler 让 app 正常退出
        if (sDefaultHandler != null) sDefaultHandler.uncaughtException(thread, throwable);
    });
    // 检查并上报之前保存的 crash log
    uploadPendingCrashes(context);
}
```

#### 2. 保存 crash 到本地文件
- 路径: `context.getFilesDir() + "/crash_logs/"` 目录
- 文件名: `{timestamp}.json`
- 内容 (JSONObject):
```json
{
  "platform": "android",
  "app_version": "获取 PackageInfo.versionName",
  "device_model": "Build.MODEL",
  "os_version": "Android " + Build.VERSION.RELEASE,
  "stacktrace": "throwable 完整 stacktrace (Log.getStackTraceString)",
  "user_action": "从 sLastUserAction 读取",
  "fatal": true,
  "timestamp": unix_seconds
}
```

#### 3. 上报到后端
```java
private static void uploadPendingCrashes(Context context) {
    // 在后台线程中运行
    ExecutorService exec = Executors.newSingleThreadExecutor();
    exec.execute(() -> {
        File dir = new File(context.getFilesDir(), "crash_logs");
        if (!dir.exists()) return;

        String token = ClawPhonesAPI.getToken(context);
        if (token == null) return; // 未登录，等下次

        for (File f : dir.listFiles()) {
            if (!f.getName().endsWith(".json")) continue;
            try {
                String json = readFile(f);
                // POST /v1/crash-reports
                ClawPhonesAPI.postCrashReport(token, json);
                f.delete(); // 上报成功删除
            } catch (Exception e) {
                // 上报失败保留，下次重试
            }
        }
    });
}
```

#### 4. 非致命错误上报
```java
public static void reportNonFatal(Context context, Throwable t, String userAction) {
    saveCrashToFile(context, t, false /* fatal=false */);
    // 去重: 同 stacktrace hash 5 分钟内不重复保存
}
```

#### 5. 用户操作追踪
```java
private static volatile String sLastUserAction = "";
public static void setLastAction(String action) { sLastUserAction = action; }
```
在关键位置调用:
- ChatActivity.onSend() → `CrashReporter.setLastAction("sending_message")`
- LoginActivity 登录点击 → `CrashReporter.setLastAction("login")`
- ConversationListActivity 加载 → `CrashReporter.setLastAction("loading_conversations")`

#### 6. ClawPhonesAPI 新增方法
```java
public static void postCrashReport(String token, String jsonBody) throws IOException, ApiException {
    // POST /v1/crash-reports, body = jsonBody string
}
```

#### 7. 初始化调用
在 `ClawPhonesLauncherActivity.onCreate()` 中加:
```java
CrashReporter.init(getApplicationContext());
```

### 约束
- 不用第三方库 (不用 Firebase Crashlytics)
- crash_logs 目录上限 50 个文件，超过删最老的
- stacktrace 截断 5000 字符
- 不阻塞主线程

### 验收标准
- [ ] App crash 后下次启动自动上报到 /v1/crash-reports
- [ ] 非致命错误 (streaming 失败等) 也能上报
- [ ] 无 token 时保留 crash log 等登录后上报
- [ ] 编译通过: JAVA_HOME=/opt/homebrew/Cellar/openjdk@17/17.0.18/libexec/openjdk.jdk/Contents/Home ./gradlew assembleDebug
