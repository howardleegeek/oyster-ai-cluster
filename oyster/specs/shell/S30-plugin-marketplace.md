---
task_id: S30-plugin-marketplace
project: shell-vibe-ide
priority: 3
estimated_minutes: 45
depends_on: ["S26-plugin-system"]
modifies: ["web-ui/app/components/plugins/marketplace.tsx", "web-ui/app/components/plugins/plugin-card.tsx", "web-ui/app/lib/plugins/plugin-registry.ts", "web-ui/app/lib/supabase/plugins.ts"]
executor: glm
---

## 目标

创建插件市场，让社区发布和安装插件。

## 开源方案

- **Verdaccio**: github.com/verdaccio/verdaccio (16k stars, MIT) — 私有 NPM 注册表
- 或直接用 NPM public registry + `shell-plugin-` 前缀

## 步骤

1. 插件注册表:
   - 数据存储: Supabase
   - 字段: id, name, version, author, description, downloads, chain_support, npm_package
2. 发布流程:
   - 开发者创建 `shell-plugin-xxx` NPM 包
   - 提交到 Shell 注册表 (通过 CLI 或 Web)
   - 审核后上架 (自动基本检查)
3. 安装流程:
   - 浏览市场
   - 一键安装 (NPM install + 自动配置)
   - 版本管理 (升级/降级)
4. 市场 UI:
   - 分类: Tools, Analysis, Deploy, UI, Chain-specific
   - 搜索 + 排序 (popular, recent, rating)
   - 每个插件: 名称 + 描述 + 星级 + 下载量 + 作者
5. 推荐插件 (内置):
   - shell-plugin-slither
   - shell-plugin-mythril
   - shell-plugin-otterscan (本地浏览器)
   - shell-plugin-whatsabi (ABI 推断)

## UI

```
┌─ Plugin Marketplace ────────────────┐
│ 🔍 Search plugins...                │
│                                      │
│ [All] [Tools] [Analysis] [Deploy]    │
│                                      │
│ ┌─ Slither Audit ─────────────────┐ │
│ │ ⭐ 4.8 | 1.2k installs         │ │
│ │ Automatic security scanning     │ │
│ │              [Install] [Details]│ │
│ └─────────────────────────────────┘ │
│                                      │
│ ┌─ Otterscan Explorer ────────────┐ │
│ │ ⭐ 4.5 | 800 installs          │ │
│ │ Local block explorer panel      │ │
│ │              [Install] [Details]│ │
│ └─────────────────────────────────┘ │
└──────────────────────────────────────┘
```

## 验收标准

- [ ] 市场页面显示可用插件
- [ ] 搜索和分类过滤工作
- [ ] 一键安装插件
- [ ] 已安装插件管理
- [ ] 插件评分系统

## 不要做

- 不要实现付费插件 (先全免费)
- 不要自建 NPM registry (用公共 NPM)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
