---
task_id: AF04-dispatch-ui
project: agentforge-v2
priority: 2
estimated_minutes: 45
depends_on: [AF02-dispatch-integration]
modifies: ["packages/ui/src/views/", "packages/ui/src/menu-items/"]
executor: glm
---
## 目标
在 AgentForge UI 中添加 Dispatch 控制面板，显示集群节点状态和任务分发

## 技术方案
1. 在 `packages/ui/src/views/` 添加 `dispatch/` 页面目录
2. DispatchDashboard 组件：显示节点列表、slots 使用率、任务队列
3. 在侧边栏菜单添加 "Dispatch" 入口
4. 调用 /api/v1/dispatch/* API 获取数据
5. 每 10s 自动刷新

## 约束
- 使用现有的 MUI (Material-UI) 组件库
- 遵循现有的 UI 设计风格
- 响应式布局
- 不新建超过 3 个文件

## 验收标准
- [ ] 侧边栏出现 "Dispatch" 菜单项
- [ ] 点击进入显示节点卡片（名称、slots、状态）
- [ ] 显示 pending/running/completed 任务计数
- [ ] npm run build 通过

## 不要做
- 不改现有页面
- 不改 Flowise 核心组件
- 不加新 npm 依赖
