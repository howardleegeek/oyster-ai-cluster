---
task_id: S01-x-article-optimize
project: article-pipeline
priority: 1
depends_on: []
modifies:
  - scripts/cdp_article_draft.py
executor: glm
---

## 目标
全面优化 X Article 自动写入流程，修复以下问题：

## 当前问题
1. CDP 直连后 X Article 编辑器 DOM 结构无法用 Playwright 标准 selector 定位
2. contenteditable 区域无法通过 click/keyboard.type 写入
3. 需找到可稳定写入的方案

## 优化方向
1. **写入方案** - 尝试:
   - clipboard paste (insert_text)
   - JavaScript 直接操作 DOM
   - CDP Runtime.evaluate 注入内容
   - keyboard.press 后跟 insert_text

2. **定位方案** - 尝试:
   - aria-label 属性定位
   - placeholder 属性定位
   - 相对位置 + click + type
   - XPath 定位 contenteditable

3. **稳定性** - 添加:
   - 重试逻辑 (3次)
   - 等待 DOM 稳定
   - screenshot 调试输出

## 验收标准
- [ ] 自动化写入 title + body 到 X Article 草稿成功
- [ ] 可通过命令行执行: python3 cdp_article_draft.py --json output/xxx.json --cdp-port 9223
- [ ] 10 次中至少 8 次成功

## 验证命令
```bash
cd ~/Downloads/article_pipeline/scripts
python3 cdp_article_draft.py --json ../output/2026-02-16_clawglasses.json --cdp-port 9223
```
