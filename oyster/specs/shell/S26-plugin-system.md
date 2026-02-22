---
task_id: S26-plugin-system
project: shell-vibe-ide
priority: 2
estimated_minutes: 60
depends_on: ["S18-web-app-deploy"]
modifies: ["web-ui/app/lib/plugins/plugin-engine.ts", "web-ui/app/lib/plugins/plugin-context.ts", "web-ui/app/components/plugins/plugin-manager.tsx", ".opencode/plugins/plugin-interface.ts"]
executor: glm
---

## 目标

创建插件系统，让社区可以扩展 Shell 的能力。

## 开源参考

- **Remix Plugin Engine**: github.com/ethereum/remix-plugin (Apache-2.0) — 最成熟的 Web3 IDE 插件系统
- **bolt.diy 的 MCP 支持** — 已有插件基础
- **VS Code Extension API** — 概念参考

## 步骤

1. 定义插件接口:
   ```typescript
   interface ShellPlugin {
     id: string;
     name: string;
     version: string;
     description: string;
     chain?: 'svm' | 'evm' | 'move' | 'all';
     activate(context: PluginContext): void;
     deactivate(): void;
   }

   interface PluginContext {
     editor: EditorAPI;      // 读写编辑器内容
     terminal: TerminalAPI;  // 输出到终端
     reports: ReportsAPI;    // 读写报告
     chain: ChainAPI;        // 链上交互
     ui: UIAPI;             // 注册面板/菜单
   }
   ```
2. 插件加载:
   - 本地: `~/.shell/plugins/` 目录
   - NPM: `pnpm add shell-plugin-xxx`
   - URL: 动态加载远程插件 (sandboxed iframe)
3. 内置插件 (重构现有功能为插件):
   - shell-plugin-slither: 安全审计
   - shell-plugin-foundry: EVM 构建测试
   - shell-plugin-anchor: SVM 构建测试
   - shell-plugin-gas-profiler: Gas 分析
4. 插件管理 UI:
   - 已安装列表
   - 启用/禁用
   - 插件设置

## 验收标准

- [ ] 插件接口定义完成
- [ ] 至少 1 个功能重构为插件
- [ ] 本地插件加载工作
- [ ] 插件管理 UI
- [ ] 插件可以注册面板

## 不要做

- 不要自己实现沙箱 (用 iframe)
- 不要实现插件市场 (S30 做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
