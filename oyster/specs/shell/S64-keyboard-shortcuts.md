---
task_id: S64-keyboard-shortcuts
project: shell-vibe-ide
priority: 2
estimated_minutes: 15
depends_on: ["S01-fork-bolt-diy"]
modifies: ["web-ui/app/lib/stores/shortcuts.ts", "web-ui/app/components/settings/KeyboardShortcuts.tsx"]
executor: glm
---

## 目标

IDE 键盘快捷键系统：为常用操作绑定快捷键，支持用户自定义。

## 步骤

1. `web-ui/app/lib/stores/shortcuts.ts`:
   - nanostores atom: `shortcuts` — Map<action, keybinding>
   - 默认快捷键:
     - Cmd/Ctrl+B: Build
     - Cmd/Ctrl+Shift+T: Test
     - Cmd/Ctrl+Shift+D: Deploy
     - Cmd/Ctrl+K: 打开 AI Chat
     - Cmd/Ctrl+Shift+E: 切换 SVM/EVM
     - Cmd/Ctrl+1: 打开文件树
     - Cmd/Ctrl+2: 打开终端
     - Cmd/Ctrl+Shift+P: 命令面板 (搜索所有操作)
   - 全局 keydown listener 注册
   - 冲突检测
2. `web-ui/app/components/settings/KeyboardShortcuts.tsx`:
   - 快捷键列表 (action + 当前绑定)
   - 点击绑定 → 进入录制模式 → 按键组合 → 保存
   - "Reset to defaults" 按钮
   - 存储到 localStorage
3. 命令面板 (Cmd/Ctrl+Shift+P):
   - 搜索框 + 操作列表
   - 模糊搜索
   - 显示快捷键

## 验收标准

- [ ] 默认快捷键可用
- [ ] 自定义快捷键可录制
- [ ] 命令面板可搜索
- [ ] 冲突检测

## 不要做

- 不要覆盖 Monaco 编辑器内置快捷键
- 不要覆盖浏览器原生快捷键 (Cmd+C, Cmd+V 等)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
