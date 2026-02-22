---
task_id: S00-master-plan
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: codex-node-1
---

## 目标
ClawMarketing 多平台 AI 运营助手 - 整体方案和实现计划

## 产品定位

**ClawMarketing = AI 多平台社交媒体运营助手**

核心理念：设置一次，AI 每天自动运营

---

## 核心功能

### 1. 多平台支持
- Twitter (x.com)
- Discord  
- Instagram
- LinkedIn

### 2. 浏览器自动化 (CDP)
- 自动发推
- 自动回复评论/私信
- 自动点赞
- 自动关注

### 3. Engagement Farming
- 自动搜索关键词并互动
- 自动追踪目标用户
- 自动回复提到

### 4. AI 内容生成
- Persona Engine: 不同人设生成不同风格内容
- Vision Agent: 分析截图理解上下文
- Quality Gate: 质量检查

---

## 技术架构

```
用户 → 前端 (Vercel)
          ↓
      后端 API (GCP codex-node-1:8000)
          ↓
      TaskQueue (Redis/SQLite)
          ↓
    ┌───┴───┐
    ↓         ↓
TwitterAgent  DiscordAgent
(CDP)       (CDP)
    ↓         ↓
浏览器       浏览器
(Mac-2)    (各平台)
```

---

## MVP 实现计划

### Phase 1: 修复基础问题 (当前优先)
- [ ] 前端登录修复 (username → email)
- [ ] 后端 API 正常响应
- [ ] 数据库初始化

### Phase 2: Twitter 发推功能
- [ ] CDP 连接 Mac-2 浏览器
- [ ] 实现发推 API
- [ ] 前端创建 Tweet 页面

### Phase 3: 多平台扩展
- [ ] LinkedIn Agent
- [ ] Instagram Agent  
- [ ] Discord Agent

### Phase 4: Engagement Farming
- [ ] 自动搜索和互动
- [ ] 自动回复

---

## 验收标准
- [ ] 用户可以注册/登录
- [ ] 可以添加社交账号
- [ ] 可以创建 AI Persona
- [ ] 可以发推测试成功

## 不要做
- 不做复杂的后台任务
- 不做完整的测试套件
- 先 MVP 再完善
