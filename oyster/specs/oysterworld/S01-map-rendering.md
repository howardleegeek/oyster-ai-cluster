---
task_id: S01-map-rendering
project: oysterworld
priority: 3
depends_on: []
modifies:
  - map/src/MapViewer.tsx
executor: glm
---

## 目标
优化地图渲染性能

## 约束
- 使用现有 Mapbox/Leaflet
- 不改数据层

## 具体改动
1. 实现地图瓦片懒加载
2. 添加离线缓存
3. 优化首屏加载
4. 写性能测试

## 验收标准
- [ ] 首屏加载 < 3s
- [ ] 地图缩放流畅
- [ ] Lighthouse Performance > 80

## 不要做
- 不改数据模型
- 不加新依赖
