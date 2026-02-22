## 目标

为 Shell 添加安全响应头，保护生产环境。

## 步骤

1. 修改 `web-ui/app/entry.server.tsx`:
   - 在 handleRequest 函数中添加安全头:
   ```typescript
   headers.set('X-Frame-Options', 'DENY');
   headers.set('X-Content-Type-Options', 'nosniff');
   headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
   headers.set('X-XSS-Protection', '1; mode=block');
   headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
   ```
   - CSP (Content-Security-Policy):
   ```
   default-src 'self';
   script-src 'self' 'unsafe-inline' 'unsafe-eval';
   style-src 'self' 'unsafe-inline';
   img-src 'self' data: https:;
   connect-src 'self' https://api.minimax.io https://api.openai.com https://api.anthropic.com wss: ws:;
   font-src 'self' data:;
   ```
   - 只在 production 环境应用 CSP (开发模式太严格会挡 HMR)

## 约束

- CSP 必须允许 WebContainer 的 WebSocket 连接
- CSP 必须允许所有 LLM provider 的 API 域名
- 开发模式下不启用 CSP
- 不要阻断现有功能

## 验收标准

- [ ] 生产环境响应包含所有安全头
- [ ] 开发环境 HMR 不受影响
- [ ] WebContainer 正常工作
- [ ] LLM API 调用不被 CSP 阻断
- [ ] npm test 通过

## 不要做

- 不要在开发模式启用严格 CSP
- 不要阻断 WebSocket 连接