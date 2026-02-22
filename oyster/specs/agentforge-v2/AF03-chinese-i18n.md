---
task_id: AF03-chinese-i18n
project: agentforge-v2
priority: 2
estimated_minutes: 30
depends_on: []
modifies: ["i18n/", "packages/ui/src/"]
executor: glm
---
## 目标
完善中文国际化支持，确保 UI 所有关键文字有中文翻译

## 技术方案
1. 检查 i18n/ 目录现有的中文翻译文件
2. 补全缺失的中文翻译 key
3. 设置默认语言为中文（可切换）
4. 确保 workflow builder 中的节点名称/描述有中文

## 约束
- 使用现有的 i18n 框架（react-i18next）
- 不改英文翻译
- 只翻译 UI 文字，不翻译技术术语

## 验收标准
- [ ] 切换到中文后，主要导航/按钮/表单标签为中文
- [ ] workflow builder 侧边栏节点分类有中文
- [ ] 设置页面可切换中英文
- [ ] npm run build 通过

## 不要做
- 不改 UI 布局
- 不改业务逻辑
- 不翻译代码注释
