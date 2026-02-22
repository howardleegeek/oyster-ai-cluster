---
task_id: S131-bluesky-adapter
project: clawmarketing
priority: 2
depends_on: ["S130-bluesky-client"]
modifies: ["backend/adapters/bluesky_adapter.py"]
executor: glm
---
## 目标
实现 Bluesky 内容适配器，300字符限制 + facets 链接

## 约束
- 300字符限制
- 支持 facets 格式链接检测
- 处理图片上传 blob
- 返回 AT Protocol 兼容 dict
- 不留 TODO/FIXME/placeholder

## 验收标准
- [ ] pytest tests/test_bluesky_adapter.py 全绿
- [ ] adapt_post() 正确处理超长内容
- [ ] detect_links() 提取 URLs 生成 facets
- [ ] adapt_image() 处理图片上传

## 不要做
- 不动 frontend
- 不留 TODO/FIXME/placeholder
