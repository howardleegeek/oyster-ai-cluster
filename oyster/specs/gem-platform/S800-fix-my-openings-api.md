---
task_id: S800-fix-my-openings-api
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/PackOpening.tsx
  - lumina/services/packApi.ts
executor: glm
---

## 目标
修复 My Openings 页面无法加载的问题

## 问题
页面显示 "Failed to load your pack openings"

## 排查
1. 检查 packApi 是否有 listOpenings 方法
2. 检查后端是否有对应 API
3. 修复前端调用

## 验收
- [ ] My Openings 页面可正常加载
