---
task_id: S70-share-snippet
project: shell-vibe-ide
priority: 3
estimated_minutes: 15
depends_on: ["S01-fork-bolt-diy"]
modifies: ["web-ui/app/components/workbench/ShareSnippet.tsx"]
executor: glm
---

## 目标

代码片段分享：选中代码 → 生成可分享的链接/图片，带赛博朋克风格语法高亮。

## 步骤

1. `web-ui/app/components/workbench/ShareSnippet.tsx`:
   - 编辑器右键菜单: "Share Snippet"
   - 获取选中代码 + 文件名 + 语言
   - 生成分享卡片 (Canvas/DOM → PNG):
     - 赛博朋克风格背景 (渐变暗色)
     - 代码语法高亮 (复用 Monaco 的 token 颜色)
     - 文件名 + 语言标签
     - Shell IDE logo 水印
     - 行号
   - 导出选项:
     - 复制为图片 (clipboard)
     - 下载 PNG
     - 复制为 Markdown 代码块
   - 使用 html2canvas 或 Canvas API (不引入新大依赖)
2. 样式:
   - 背景: linear-gradient(135deg, #0a0a0f, #1a1a2e)
   - 边框: 1px solid #00ff8833
   - 字体: JetBrains Mono / monospace

## 验收标准

- [ ] 选中代码可生成卡片
- [ ] PNG 导出可用
- [ ] Markdown 复制可用
- [ ] 赛博朋克风格正确

## 不要做

- 不要实现云端分享链接 (只做本地导出)
- 不要引入 carbon.now.sh API (离线生成)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
