---
task_id: S46-upgrade-ui-shadcn-all
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: claude
---

## 目标
升级所有页面UI到shadcn/ui组件库

## 当前问题
- 页面使用基础Tailwind CSS
- 需要升级到shadcn/ui生产级组件

## 具体改动
1. 安装shadcn/ui到frontend项目
2. 添加常用组件:
   - Button, Card, Input, Textarea
   - Select, Checkbox, Dialog
   - Table, Badge, Avatar
   - Form组件
3. 改造以下页面使用shadcn/ui:
   - Dashboard.tsx - 使用Card, Button组件
   - Scout.tsx - 使用Card, Badge, Button组件
   - Content.tsx - 使用Table, Badge组件
   - AgentControl.tsx - 使用Card, Table, Badge组件
   - Login.tsx, Register.tsx - 使用Card, Input, Button组件

## 验收标准
- [ ] shadcn/ui安装成功
- [ ] 常用组件可用
- [ ] 所有页面使用shadcn/ui组件
- [ ] UI更专业美观

## 不要做
- 不改变功能逻辑
- 不改API调用
