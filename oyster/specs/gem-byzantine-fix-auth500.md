# GEM Backend: Complete AuthService Implementation + Byzantine Verification

## 背景
AuthService 方法是 GLM 生成的骨架，依赖注入链未完整接通。
拜占庭测试两节点一致 500。不是 bug — 是未完成的实现。

## 任务

### Phase 1: 诊断 (在 codex-node-1)
```bash
gcloud compute ssh codex-node-1 --zone=us-west1-b
cd ~/gem-platform/backend && source venv/bin/activate
```
1. `tail -100 /tmp/uvicorn.log` 看具体 traceback
2. Python REPL 测试依赖注入链:
   - AuthService.__init__ 需要什么参数?
   - get_auth_service 能否成功构造 AuthService?
   - auth_cache (Redis) 的方法存在吗? save_wallet_nonce, consume_wallet_nonce 等
   - user_repo 的方法存在吗? get_user_by_wallet, create_user 等
   - send_mail (plib) 存在吗?

### Phase 2: 补全缺失实现
可能缺失的:
- `app/db/auth_cache.py` — Redis 操作方法 (nonce, OTP hash, rate limit)
- `app/db/user.py` — UserRepo 的 CRUD 方法
- `app/plib/` — send_mail 邮件发送
- `app/services/auth.py` — AuthService 方法内部逻辑
- `app/utils.py` — SuccessResp 等工具类
- DI 注入: get_auth_service, get_user_repo 等 Depends 函数

原则: 让 wallet/challenge 和 email/otp/send 跑通。
email 实际发送可以 DEV 环境跳过 (print 代替 SendGrid)。

### Phase 3: 修复并验证
1. 修好后重启 uvicorn
2. 测试:
   ```bash
   # wallet challenge 应返回 nonce + message + expires_at
   curl -X POST http://localhost:8000/auth/wallet/challenge \
     -H "Content-Type: application/json" \
     -d '{"wallet_address":"DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy"}'

   # email OTP 应返回 200 (DEV 可以 skip 实际发送)
   curl -X POST http://localhost:8000/auth/email/otp/send \
     -H "Content-Type: application/json" \
     -d '{"email":"test@gem.io"}'
   ```

### Phase 4: 拜占庭验证
1. SCP 所有修改的文件到 glm-node-2
2. 两节点都跑 `bash ~/gem-test-quick.sh`
3. 结果必须一致，wallet challenge 返回 nonce，不再 500

## 环境
- codex-node-1: SSH via `gcloud compute ssh codex-node-1 --zone=us-west1-b`
- glm-node-2: SSH via `gcloud compute ssh glm-node-2 --zone=us-west1-b`
- 两节点都有: venv, MySQL (gem_rwa, 22 tables), Redis, .env
- 测试脚本: ~/gem-test-quick.sh

## Repo
- 本地: ~/gem-platform/backend/
- GitHub: The-world-is-your-Oyster/gem-platform (main branch)

## 修完后
- git commit 所有修改
- git push origin main
- 两节点 gem-test-quick.sh 结果贴出来
