---
task_id: S05-community-management
project: clawphones-admin
priority: 1
depends_on: []
modifies:
  - ~/Downloads/clawphones-admin/src/app/communities/
  - ~/Downloads/clawphones-admin/src/components/communities/
executor: glm
---

## 目标
创建社区管理页面 (Sprint 13)

## 约束
- 使用 shadcn/ui
- 对接 /v1/communities/* API

## 具体改动

### 1. 创建 Communities 页面
创建 ~/Downloads/clawphones-admin/src/app/communities/page.tsx:
- CommunityList - 社区列表
- CommunityDetail - 详情

### 2. 创建组件
创建 ~/Downloads/clawphones-admin/src/components/communities/:
- CommunityList.tsx
- CommunityCard.tsx
- MemberList.tsx

### 3. 功能
- GET /v1/communities - 列表
- POST /v1/communities - 创建
- GET /v1/communities/{id} - 详情
- POST /v1/communities/{id}/join - 加入
- DELETE /v1/communities/{id}/members/{user_id} - 移除成员

### 4. UI
- Card (社区卡片)
- Avatar (成员头像)
- Map (可选 - 社区位置)

## 验收标准
- [ ] /communities 页面可访问
- [ ] 社区列表显示
- [ ] 可创建社区

## 不要做
- 不修改 backend
