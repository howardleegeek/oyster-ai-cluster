## 任务: ClawPhones 全面测试执行

### 背景
ClawPhones S2-S20 全部完成，22,000+ 行代码。需要跑完整测试验证代码质量。

### 目标
在 GCP 节点上拉取最新代码，安装依赖，跑全部测试。

### 步骤

1. Clone repo:
   ```
   git clone https://github.com/howardleegeek/openclaw-mobile.git /tmp/clawphones-test
   cd /tmp/clawphones-test
   ```

2. Backend (proxy/) 测试:
   ```
   cd proxy
   python3 -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn httpx aiosqlite bcrypt h3 pydantic pytest pytest-asyncio python-multipart
   MOCK_MODE=1 ADMIN_KEY=test python3 -m pytest test_api.py tests/ -v --tb=short
   ```

3. Relay (server.s11-6.js) 语法 + 基础测试:
   ```
   cd /tmp/clawphones-test
   node -c server.s11-6.js
   # 如果有 package.json → npm install && npm test
   ```

4. Android 编译检查 (Java 语法):
   ```
   find android/ -name "*.java" -exec javac -d /dev/null {} + 2>&1 | head -50
   # 或者用 javap 检查语法
   ```

5. iOS Swift 语法检查:
   ```
   find ios/ -name "*.swift" -exec swiftc -typecheck {} + 2>&1 | head -50
   ```

### 验收标准
- [ ] pytest 全部 PASS (或记录哪些 FAIL + 原因)
- [ ] JS syntax check PASS
- [ ] 编译检查结果记录

### 产出
写结果到 `/tmp/clawphones-test-results.md`
