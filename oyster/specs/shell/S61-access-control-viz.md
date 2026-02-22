---
task_id: S61-access-control-viz
project: shell-vibe-ide
priority: 3
estimated_minutes: 25
depends_on: ["S14-security-audit"]
modifies: ["web-ui/app/components/workbench/AccessControlViz.tsx"]
executor: glm
---

## 目标

访问控制可视化：从合约代码解析 onlyOwner / AccessControl / Ownable 修饰符，生成角色-函数权限矩阵图。

## 步骤

1. `web-ui/app/components/workbench/AccessControlViz.tsx`:
   - 解析当前合约代码 (正则匹配):
     - `onlyOwner` modifier
     - `onlyRole(ROLE_NAME)` modifier
     - `require(msg.sender == ...)` 检查
     - OpenZeppelin AccessControl 的 `hasRole`
   - 生成权限矩阵:
     - 行: 角色 (Owner, Admin, Minter, Pauser, DEFAULT_ADMIN...)
     - 列: 函数名
     - 单元格: ✅ 有权限 / ❌ 无权限
   - 用 HTML table 渲染 (不引入图表库)
   - 高亮无保护的 external/public 函数 (黄色警告)
   - 检测 Anchor 程序的 `#[access_control]` 和 `constraint`
2. 放在安全审计面板的子 tab

## 验收标准

- [ ] 检测 onlyOwner 修饰符
- [ ] 检测 AccessControl 角色
- [ ] 矩阵正确渲染
- [ ] 无保护函数有警告

## 不要做

- 不要用第三方图表库 (HTML table 够用)
- 不要实现 AST 解析 (正则够用)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
