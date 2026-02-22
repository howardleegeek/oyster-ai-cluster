---
task_id: S50-contract-upgrade-wizard
project: shell-vibe-ide
priority: 2
estimated_minutes: 35
depends_on: ["S10-deploy", "S21-contract-interaction"]
modifies: ["web-ui/app/components/workbench/UpgradeWizard.tsx", "web-ui/app/lib/stores/upgrade.ts", "templates/upgrade/"]
executor: glm
---

## 目标

提供合约升级向导：支持 Transparent Proxy、UUPS、Beacon 三种模式，自动生成升级脚本。

## 步骤

1. `templates/upgrade/` 下新建三个模板:
   - `TransparentProxy.sol.template`
   - `UUPSProxy.sol.template`
   - `BeaconProxy.sol.template`
2. `web-ui/app/lib/stores/upgrade.ts`:
   - `upgradeMode`: transparent | uups | beacon
   - `upgradeStatus`: idle | generating | deploying | done
3. `web-ui/app/components/workbench/UpgradeWizard.tsx`:
   - Step 1: 选择升级模式 (3 个卡片)
   - Step 2: 选择要升级的合约
   - Step 3: 预览生成的 proxy + 升级脚本
   - Step 4: 一键部署 (调用 S10 deploy)
4. Remix route `api.upgrade.ts`:
   - POST: 根据模式 + 合约生成升级代码

## 验收标准

- [ ] 三种 proxy 模式可选
- [ ] 生成的合约代码可编译
- [ ] 升级脚本包含 storage layout 检查提示
- [ ] UI 步骤流畅

## 不要做

- 不要实现自动 storage layout 对比 (S41 做)
- 不要连主网
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
