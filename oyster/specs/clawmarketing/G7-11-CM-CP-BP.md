---
task_id: G7-11-CM-CP-BP
project: clawmarketing
priority: 2
depends_on: ["G7-01-CM-BP", "G7-05-CP-CM"]
modifies: ["src/services/mobile_social.py", "src/api/mobile_publish.py"]
executor: glm
---
## 目标
移动端一键创建社交媒体营销活动

## 技术方案
1. 新增 `MobileSocialPublisher` 服务，暴露简易 API
2. 支持从 CP 创建 -> CM 编排 -> BP 发布全流程
3. 模板化内容：快速创建新品发布、活动预告
4. 移动端推送发布结果通知

## 约束
- 复用 CM 现有发布逻辑
- 不修改 CP UI
- 在现有代码库内修改，不新建超过3个文件
- 不留 TODO/FIXME/placeholder
- 写基础测试

## 验收标准
- [ ] 移动端发布 < 10s
- [ ] 支持草稿/发布两种模式
- [ ] pytest 全绿

## 不要做
- 不重构现有代码
- 不改 UI/CSS
