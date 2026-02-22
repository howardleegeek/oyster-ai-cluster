# Task C2: PackOpening 组件接入后端

## 目标
修改 PackOpening 组件，使其展示后端返回的真实开包结果，而非客户端随机生成。

## 前提
- Task C1 已完成（PackStoreView 调用 packApi 获取开包结果）

## 文件
- `lumina/components/PackOpening.tsx`

## 当前状态
PackOpening 接收 props 并展示开包动画。需要确认当前的 props 接口。

## 修改要点

### 1. Props 接口更新
```typescript
interface PackOpeningProps {
  items: VaultItemResp[];  // 后端返回的真实 items
  onClose: () => void;
  packName?: string;
}
```

### 2. 展示后端数据
- 每个 item 展示: name, rarity, image_url, fmv (Fair Market Value)
- 使用后端返回的 rarity 等级决定动画效果（Legendary 更华丽）
- 不再使用 Math.random() 或本地 gem 生成逻辑

### 3. 类型对齐
确保使用的类型与后端 schema 匹配:
```typescript
interface VaultItemResp {
  id: number;
  rarity: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  fmv: number;
  metadata: string; // JSON string
  status: string;
  created_at: string;
}
```

## 验证
1. TypeScript 编译无错误
2. 开包后动画正确显示后端返回的 items
