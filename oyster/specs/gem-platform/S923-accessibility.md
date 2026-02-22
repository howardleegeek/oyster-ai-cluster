---
task_id: S923-accessibility
project: gem-platform
priority: 1
depends_on: []
modifies:
  - lumina/components/Navbar.tsx
---

## 目标
Improve accessibility (a11y) for better UX

## 约束
- 不改变视觉设计
- 遵循 WCAG 2.1 AA 标准

## 具体改动
1. Add proper ARIA labels to interactive elements
2. Add keyboard navigation support
3. Ensure color contrast meets WCAG AA (4.5:1 for text)
4. Add focus indicators for keyboard users

## 验收标准
- [ ] No ARIA errors in console
- [ ] Keyboard navigation works
