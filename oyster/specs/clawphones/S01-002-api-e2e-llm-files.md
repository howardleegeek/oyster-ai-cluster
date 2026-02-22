---
task_id: S01-002
project: clawphones
priority: 1
depends_on: ["S01-001"]
modifies: ["proxy/test_api.py"]
executor: glm
---

## 目标
后端 API 端对端测试：多 tier LLM 路由、文件上传、导出功能

## 约束
- Python pytest
- 覆盖 LLM 路由与文件处理

## 具体改动
- 完善 proxy/test_api.py，添加：
  - `/v1/chat/completions` 多 tier 路由测试（free→DeepSeek, pro→Kimi, max→Claude）
  - `/v1/upload` 文件上传测试
  - `/v1/conversations/{id}/upload` 会话文件上传测试
  - `/v1/user/export` 数据导出测试

## 验收标准
- [ ] LLM 路由测试通过
- [ ] 文件上传/下载测试通过
- [ ] 数据导出测试通过
