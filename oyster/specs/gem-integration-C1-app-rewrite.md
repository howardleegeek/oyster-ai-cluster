# Task C1: App.tsx 重构 — 接入后端集成组件

## 目标
重写 App.tsx，用后端集成版组件替换 mock 版本，接入 AuthGate 实现登录门控。

## 前提
- Task B1-B4 已完成（API 层修复、路径对齐、AuthContext 可用）
- Task A1-A2 已完成（后端 API 可调用）

## 文件
- `lumina/App.tsx` — 主要重写
- `lumina/index.tsx` — 已在 B4 中添加 AuthProvider

## 当前 App.tsx 结构 (需替换)
```
- 硬编码 PACKS 数组 (4 个 pack)
- 硬编码 POTENTIAL_HITS 数组 (8 个 gem)
- 本地 state: credits, inventory, view, selectedPack, isOpening, openedItems
- Math.random() 生成开包结果
- Navbar (旧版), Dashboard (旧版), Marketplace (旧版)
```

## 新 App.tsx 设计

```tsx
import { useState, useEffect } from 'react';
import { useAuth } from './contexts/AuthContext';
import AuthGate from './components/AuthGate';
import NavbarUpdates from './components/NavbarUpdates';
import PackStoreView from './components/PackStoreView'; // 新建或从 App.tsx 提取
import DashboardUpdates from './components/DashboardUpdates';
import MarketplaceUpdates from './components/MarketplaceUpdates';
import WalletPanel from './components/WalletPanel';
import OrderPanel from './components/OrderPanel';
import ReferralPanel from './components/ReferralPanel';
import Leaderboard from './components/Leaderboard';
import AdminPanel from './components/AdminPanel';
import PackOpening from './components/PackOpening';

type ViewState = 'PACKS' | 'DASHBOARD' | 'MARKETPLACE' | 'WALLET' | 'ORDERS' | 'REFERRAL' | 'LEADERBOARD' | 'ADMIN';

function App() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [view, setView] = useState<ViewState>('PACKS');

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <AuthGate>
      <div className="app">
        <NavbarUpdates currentView={view} setView={setView} />

        <main>
          {view === 'PACKS' && <PackStoreView />}
          {view === 'DASHBOARD' && <DashboardUpdates />}
          {view === 'MARKETPLACE' && <MarketplaceUpdates />}
          {view === 'WALLET' && <WalletPanel />}
          {view === 'ORDERS' && <OrderPanel />}
          {view === 'REFERRAL' && <ReferralPanel />}
          {view === 'LEADERBOARD' && <Leaderboard />}
          {view === 'ADMIN' && user?.role === 'admin' && <AdminPanel />}
        </main>
      </div>
    </AuthGate>
  );
}

export default App;
```

## Pack Store View (从 App.tsx 提取)

创建 `lumina/components/PackStoreView.tsx`:
- 从 `packApi.listPacks()` 获取 pack 列表（不用硬编码 PACKS）
- 选择 pack → `packApi.purchasePack(packId, { quantity: 1 })` → 获得 opening_id + 支付信息
- 用户通过 Solana 支付 → 获得 tx_hash
- `packApi.confirmPayment(openingId, { tx_hash })` → 获得开包结果
- 显示 PackOpening 动画

关键流程:
```typescript
// 1. 用户选择 pack
const purchaseResp = await packApi.purchasePack(packId, { quantity: 1 });
// purchaseResp: { opening_id, amount_sol, receiver_wallet, quote_expires_at }

// 2. 发送 Solana 支付
const txHash = await sendSolPayment(purchaseResp.receiver_wallet, purchaseResp.amount_sol);

// 3. 确认支付，获得开包结果
const confirmResp = await packApi.confirmPayment(purchaseResp.opening_id, { tx_hash: txHash });
// confirmResp 包含开出的 items

// 4. 显示开包动画
setOpenedItems(confirmResp.items);
setIsOpening(true);
```

## NavbarUpdates 适配

NavbarUpdates 可能需要接受 `currentView` 和 `setView` props。检查其当前 props 接口，如果不支持 view 切换，需要添加:

```typescript
interface NavbarUpdatesProps {
  currentView: ViewState;
  setView: (view: ViewState) => void;
}
```

确保 Navbar 有导航按钮: Packs, Dashboard, Marketplace, Wallet, Orders, Referral, Leaderboard, Admin。

## AuthGate 适配

检查 AuthGate.tsx 的 `useAuth()` 调用是否与 AuthContext 匹配。确保:
- 未登录 → 显示登录界面（钱包连接 or Email OTP）
- 已登录 → 渲染 children

## 删除的内容
- 硬编码 PACKS 数组
- 硬编码 POTENTIAL_HITS 数组
- Math.random() 开包逻辑
- 本地 credits state（从 AuthContext 或后端获取）
- 旧版 Navbar, Dashboard, Marketplace import

## 验证
1. TypeScript 编译: `cd lumina && npx tsc --noEmit`
2. `npm run dev` 启动后页面不白屏
3. 未登录 → 显示 AuthGate 登录界面
4. 登录后 → 显示 Packs 页面，数据来自后端
