# Task B4: AuthContext 修复 + index.tsx 接入

## 目标
修复 AuthContext 中的环境变量引用错误，并在 index.tsx 中添加 AuthProvider。

## 文件

### 1. `lumina/contexts/AuthContext.tsx`

**修复环境变量** — 搜索所有 `process.env.REACT_APP_API_URL` 或 `process.env.REACT_APP_*`：
```typescript
// Before (CRA 风格)
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// After (Vite 风格)
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```

**检查 AuthContext 提供的功能**（应该已有）:
- `useAuth()` hook
- `user` state (UserPrincipal or null)
- `isAuthenticated` boolean
- `isLoading` boolean
- `login()` / `walletSignLogin()` — 钱包登录
- `logout()`
- `accessToken` — 当前 token

**检查 token 存储 key 与 gemApi.ts 是否一致**:
- gemApi.ts 使用: `gem_access_token`, `gem_refresh_token`, `gem_wallet_address`
- AuthContext 应使用相同的 key

如果 AuthContext 和 gemApi.ts 的 token 存储有冲突（两套系统），需要统一。推荐方案：AuthContext 使用 gemApi.ts 的 `tokenManager` 来管理 token，不要自己维护一套。

### 2. `lumina/index.tsx`

当前内容:
```tsx
import { WalletProvider } from './contexts/WalletContext';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WalletProvider>
      <App />
    </WalletProvider>
  </React.StrictMode>
);
```

修改为:
```tsx
import { WalletProvider } from './contexts/WalletContext';
import { AuthProvider } from './contexts/AuthContext';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WalletProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </WalletProvider>
  </React.StrictMode>
);
```

注意：WalletProvider 必须在 AuthProvider 外层，因为 AuthContext 需要读取 wallet 信息。

## 验证
1. TypeScript 编译: `cd lumina && npx tsc --noEmit`
2. `grep -n "process.env" lumina/contexts/AuthContext.tsx` — 应为空（无 CRA 风格引用）
3. `grep -n "AuthProvider" lumina/index.tsx` — 确认已添加
