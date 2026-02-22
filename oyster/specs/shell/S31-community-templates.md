---
task_id: S31-community-templates
project: shell-vibe-ide
priority: 3
estimated_minutes: 40
depends_on: ["S16-template-gallery", "S24-user-auth"]
modifies: ["web-ui/app/**/*.tsx", "templates/registry.json"]
executor: glm
---

## 目标

让用户发布和分享自己的合约模板，形成社区模板市场。

## 开源方案

- **Supabase**: 存储模板数据
- **GitHub Gist API**: 存储模板代码
- **IPFS (Pinata)**: 去中心化存储 (可选)

## 步骤

1. 发布模板:
   - 用户在 IDE 中开发合约 → 点击 "Publish as Template"
   - 填写: 名称, 描述, 链, 分类, 标签
   - 代码存储到 GitHub Gist 或 Supabase Storage
   - 元数据存入 Supabase
2. 模板画廊扩展:
   - [Official] [Community] tab 切换
   - 社区模板按 stars/forks/downloads 排序
   - 模板预览 (代码 + README)
3. 模板互动:
   - Star (收藏)
   - Fork (基于此模板创建新项目)
   - 评论/评分
4. 模板审核:
   - 自动安全扫描 (Slither/Clippy)
   - 社区举报
   - 管理员审核队列

## 验收标准

- [ ] 用户可以发布模板
- [ ] 社区模板在画廊中显示
- [ ] Star/Fork 功能
- [ ] 模板搜索和过滤
- [ ] 自动安全扫描

## 不要做

- 不要实现付费模板
- 不要实现模板版本管理 (先只有最新版)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
