---
task_id: S15-remix-compiler
project: shell-vibe-ide
priority: 2
estimated_minutes: 40
depends_on: ["S05-build-integration"]
modifies: ["web-ui/package.json", "web-ui/app/**/*.ts"]
executor: glm
---

## 目标

集成 @remix-project/remix-solidity 实现浏览器内 Solidity 编译，支持多编译器版本切换。

## 步骤

1. 安装: `pnpm add @remix-project/remix-solidity @remix-project/remix-analyzer`
2. 创建 Solidity 编译服务:
   - 加载 solc 编译器 (从 CDN 或本地)
   - 支持版本选择: 0.8.x 系列
   - 编译选项: optimization, runs, evm version
3. 编译结果:
   - ABI
   - Bytecode
   - 源码映射
   - 编译错误/警告
4. 集成 remix-analyzer:
   - 编译后自动运行静态分析
   - 检测常见问题 (gas 浪费, 安全隐患)
5. UI:
   - 编译器版本选择器 (下拉菜单)
   - 编译输出面板 (ABI viewer)
   - 编译错误内联显示
6. 这是 Web App 版的编译方案 (不依赖本地 forge)

## 验收标准

- [ ] `@remix-project/remix-solidity` 安装成功
- [ ] 可在浏览器内编译 Solidity 代码
- [ ] 支持切换 solc 版本
- [ ] 编译错误显示在编辑器中
- [ ] ABI 输出可查看
- [ ] remix-analyzer 结果显示

## 不要做

- 不要替换本地 forge build (这是补充，不是替代)
- 不要实现调试器 (S19 做)
- 不要写 TODO/FIXME 注释，所有功能必须完整实现
- 路径用 web-ui/app/ (bolt.diy Remix 架构)，不是 web-ui/app/
