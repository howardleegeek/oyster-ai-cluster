---
task_id: S08-TELOS-EDITOR-FRONTEND
project: clawmarketing
priority: 1
depends_on: [S03-BRAND-TELOS-API]
modifies:
  - frontend/src/pages/TelosEditor.tsx
  - frontend/src/App.tsx
executor: glm
---

## 目标
实现前端 TELOS 编辑器组件

##具体改动
1. 新建 frontend/src/pages/TelosEditor.tsx
2. 6 个编辑区块:
   - Mission: 单行输入
   - Goals: 可添加/删除的目标列表
   - Voice: tone 下拉 + personality tags + taboos 列表
   - Strategy: 平台选择 + 频率 + 内容配比
   - Challenges: 挑战列表
   - Narratives: 核心话术列表
3. API: PUT /brands/{id}/telos | GET /brands/{id}/telos
4. 保存后显示 toast 提示

## 验收标准
- [ ] 能编辑并保存 TELOS
- [ ] 保存后刷新数据正确回显
- [ ] eslint 检查通过
- [ ] 不改现有 UI 样式

## 不要做
- 不改现有组件样式
