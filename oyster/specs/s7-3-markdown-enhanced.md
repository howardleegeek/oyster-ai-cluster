## 任务: S7-3 Markdown 渲染增强

### 背景
AI 回复经常包含表格、列表、链接等 Markdown 元素，需要完整渲染。

### 具体要求

#### 双端
1. **表格**: 正确渲染 Markdown 表格 (| 分隔), 可水平滚动
2. **有序/无序列表**: 正确缩进和标号
3. **链接**: 可点击，在系统浏览器中打开
4. **LaTeX/数学公式**: 基础支持 (inline `$...$` 和 block `$$...$$`)
5. **引用块**: `>` 引用显示为侧边线 + 灰底
6. **分隔线**: `---` 渲染为水平线

#### iOS 特殊
- 可以使用 `swift-markdown-ui` 库如果 S2-2 已引入
- 或增强现有 `AttributedString(markdown:)` 处理

#### Android 特殊
- 使用 `Markwon` 库 或手动正则解析
- 表格可能需要 HorizontalScrollView 包裹

### 文件
- iOS: `MessageRow.swift`
- Android: `ChatActivity.java` + message rendering

### 验收标准
- [ ] 表格正确显示且可横向滚动
- [ ] 列表正确缩进
- [ ] 链接可点击且在浏览器打开
- [ ] 引用块有视觉区分
- [ ] 编译通过 (双端)
