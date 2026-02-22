---
task_id: S602-referral-leaderboard-enhance
project: gem-platform
priority: 1
depends_on: []
modifies:
  - backend/app/api/referral.py (EXTEND)
  - backend/app/api/rank.py (EXTEND)
  - lumina/components/ReferralPanel.tsx (UPDATE)
  - lumina/components/Leaderboard.tsx (UPDATE)
executor: glm
---

## 目标
完善 Referral 推荐系统和 Leaderboard 排行榜

## 约束
- 文件已存在，需要扩展功能
- 使用现有框架
- 不改其他页面

## 现有文件
- backend/app/api/referral.py - 已存在
- lumina/components/ReferralPanel.tsx - 已存在
- lumina/components/Leaderboard.tsx - 已存在

## Referral 完善

### 后端
1. **推荐奖励**
   - 推荐人获得奖励 (购买折扣/积分)
   - 被推荐人获得首单优惠

2. **推荐统计**
   - 推荐人数
   - 成功转化数
   - 获得奖励

3. **邀请链接**
   - 生成唯一推荐码
   - 追踪来源

### 前端
- 完善 ReferralPanel 展示
- 推荐进度
- 奖励说明

## Leaderboard 完善

### 后端
1. **排行榜类型**
   - 收藏总值
   - 开盒数量
   - 交易次数
   - 推荐人数

2. **时间周期**
   - 每周排行
   - 每月排行
   - 全部时间

3. **奖励**
   - 每周 top 获得奖励
   - 徽章系统

### 前端
- 完善 Leaderboard 展示
- 时间筛选
- 个人排名高亮

## 约束
- 使用现有框架
- 不改其他页面

## 验收
- [ ] Referral 奖励系统完整
- [ ] Leaderboard 多维度排行
- [ ] 前端展示完善
