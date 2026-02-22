---
task_id: S06-pack-opening-animation
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/PackOpening.tsx
  - lumina/index.html
executor: glm
---

## 目标
升级开包动画，创造激动人心的抽卡体验。

## 当前状态
现有动画：3秒加载 + "DECRYPTING ASSETS..." 文字 + 直接显示卡牌网格

## 改进内容

### 1. 阶段一：升级揭示动画结构 (PackOpening.tsx)
- 改为逐卡揭示机制
- 每个卡牌有独立的揭示状态

### 2. 阶段二：稀有度发光效果
基于 Codex 建议：
- Common: 灰色微光
- Rare: 蓝色发光 `shadow-[0_0_30px_rgba(59,130,246,0.3)]`
- Epic: 紫色发光 `shadow-[0_0_40px_rgba(168,85,247,0.4)]`
- Legendary: 金色强发光 `shadow-[0_0_60px_rgba(245,158,11,0.5)]` + 脉冲动画

### 3. 阶段三：揭示时序
- 第一张卡：立即显示
- 每张后续卡：间隔 0.8-1.2秒
- Legendary 卡：揭示前 1.5秒暂停 + 放大效果

### 4. 添加 CSS 动画 (index.html)
```css
@keyframes card-reveal {
  0% { transform: scale(0.8) rotateY(90deg); opacity: 0; }
  50% { transform: scale(1.1) rotateY(0deg); opacity: 1; }
  100% { transform: scale(1) rotateY(0deg); opacity: 1; }
}

@keyframes legendary-glow {
  0%, 100% { box-shadow: 0_0_40px rgba(245,158,11,0.4); }
  50% { box-shadow: 0_0_80px rgba(245,158,11,0.7); }
}

@keyframes rarity-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

### 5. 揭示流程
```
1. INIT: 等待 revealedItems
2. OPENING: 显示 pack 动画 (保持)
3. REVEAL_START: 开始逐卡揭示
   - 按稀有度排序揭示 (Common → Legendary)
   - 每张卡 0.8s 间隔
   - Legendary 前暂停 + 特效
4. REVEAL_COMPLETE: 显示全选 + 操作按钮
```

## 验收标准
- [ ] 卡牌逐个揭示，不是同时出现
- [ ] Legendary 卡有金色发光效果
- [ ] 有揭示动画过渡效果
- [ ] 整体揭示流程 3-5秒（取决于卡牌数量）
