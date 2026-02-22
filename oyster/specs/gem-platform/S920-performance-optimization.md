---
task_id: S920-performance-optimization
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/vite.config.ts
  - lumina/package.json
---

## 目标
Optimize frontend performance with code splitting and lazy loading

## 约束
- 不改变 UI 外观
- 不添加新依赖

## 具体改动
1. Add React.lazy() and Suspense for heavy components (Marketplace, Dashboard, Vault)
2. Configure Vite for better chunk splitting
3. Add dynamic imports for route-based code splitting

## 验收标准
- [ ] Build succeeds without errors
- [ ] Bundle size reduced (main chunk < 500KB)
