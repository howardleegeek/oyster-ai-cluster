## 任务: S7-2 文件分享

### 背景
用户可能想分享 PDF、文档等文件让 AI 分析内容。

### 具体要求

#### 后端
1. 扩展 `/v1/upload` 支持: pdf, txt, csv, json, md (最大 20MB)
2. PDF/文本类文件: 提取文本内容，作为 context 发送给 AI
3. 返回格式增加 `content_text` 字段 (提取的文本)

#### 双端
1. 文件选择器 (Document Picker / file chooser)
2. 上传进度条
3. 文件类型图标显示在消息中 (PDF 图标、TXT 图标等)
4. 文件名和大小显示

### 文件
- 后端: `server.py`
- Android: `ChatActivity.java`
- iOS: `ChatInputBar.swift`, `MessageRow.swift`

### 验收标准
- [ ] 选择 PDF → 上传 → AI 回答文件内容相关问题
- [ ] 文件在消息中显示为卡片 (图标 + 文件名 + 大小)
- [ ] 上传有进度指示
- [ ] 不支持的文件类型给出提示
- [ ] 编译通过 (双端)
