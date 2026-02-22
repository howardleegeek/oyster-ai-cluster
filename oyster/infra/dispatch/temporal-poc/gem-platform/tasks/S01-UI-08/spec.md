## 目标
重构 GEM Platform 页面 (Leaderboard, Referral, Admin)，打造 Web3 社交平台的高级感

## 约束
- 不改后端 API 逻辑
- 不改功能流程，只提升视觉

## 具体改动

### LeaderboardPage.tsx (排行榜)
- **美学方向**: Web3 竞赛感 (Competitive Arena)
- **设计要点**:
  - 排名列表: 大数字排名，卡片式设计
  - Top 3: 特殊的高亮样式，金银铜配色
  - 用户信息: avatar + name + score
  - 动画: 排名变化有过渡

### ReferralPage.tsx (邀请)
- **美学方向**: 邀请奖励 (Referral Rewards)
- **设计要点**:
  - Hero: 邀请奖励说明，大字标题
  - 链接复制: 优雅的 input + button 组合
  - 统计: 邀请人数，已获得奖励

### Admin 页面
- **美学方向**: 仪表盘 (Dashboard)
- **设计要点**:
  - 侧边栏: 导航
  - 内容区: 表格或表单

## 验收标准
- [ ] 排行榜有竞赛感
- [ ] 邀请页面突出奖励
- [ ] Admin 页面专业
- [ ] 整体风格现代 Web3