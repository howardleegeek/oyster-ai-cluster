## 任务: iOS 消息时间戳 + 复制反馈 + 思考指示器优化

### 背景
iOS app 已有较好架构，但缺少几个影响体验的细节：消息无时间戳、复制无反馈、AI 思考状态不够明显。

### 具体要求

#### 1. 消息时间戳 (MessageRow.swift)
- 在每条消息 bubble 下方右侧显示时间:
  - 格式: "14:30" (当天) / "昨天 14:30" / "2/10 14:30" (更早)
  - 字体: .caption2, 颜色: .secondary
  - 只在消息间隔 > 5 分钟时显示（连续快速对话不显示每条的时间）
- Message model 已有 `createdAt: Date` 字段，直接使用

#### 2. 复制反馈 (MessageRow.swift)
- 用户长按消息选择 "Copy" 后:
  - 触发 haptic feedback: `UIImpactFeedbackGenerator(style: .medium).impactOccurred()`
  - 显示临时 toast: "已复制" (1.5 秒后自动消失)
  - toast 样式: 小型 capsule 形状，半透明黑色背景 + 白色文字，屏幕底部居中
- 实现: 在 ChatView 层添加一个 @State showCopiedToast，MessageRow 通过回调触发

#### 3. 思考指示器增强 (ChatView.swift / MessageRow.swift)
- 当前: 空消息显示 ThinkingIndicator (3 个圆点)
- 增强:
  - 在 3 个圆点下方加文字 "正在思考..."
  - 圆点动画改为顺序弹跳（如果当前没有动画的话）
  - 如果已经有动画效果，保持不变，只加文字

#### 4. 对话列表优化 (ConversationListView.swift)
- 每个对话 item 显示最后一条消息的预览 (truncated to 1 line)
  - 如果 ConversationSummary model 没有 lastMessage 字段，从 title 推导或显示 message_count
- 对话 item 显示相对时间: "刚刚" / "5分钟前" / "2小时前" / "昨天" / "2月10日"
- 下拉刷新增加 haptic feedback

### 文件清单
- 修改: `MessageRow.swift`, `ChatView.swift`, `ConversationListView.swift`
- 可能修改: `ChatViewModel.swift` (传递 toast callback)
- 新增: 无 (toast 可以用 overlay 实现，不需要新文件)

### 样式规范
- 时间戳: .caption2, Color.secondary, padding(.top, 2)
- Toast: Capsule 背景 Color.black.opacity(0.7), 白色文字, padding(8, 16)
- 思考文字: .caption, Color.secondary, "正在思考..."
- 保持现有配色，不引入新颜色

### 验收标准
- [ ] 消息间隔 > 5 分钟时显示时间戳
- [ ] 复制消息后有 haptic + toast 反馈
- [ ] AI 回复前显示思考指示器 + "正在思考..." 文字
- [ ] 对话列表显示相对时间
- [ ] 所有改动不影响现有 streaming 功能
- [ ] 无编译错误，SwiftUI preview 正常

### 注意
- iOS 最低版本 iOS 15，注意 API 兼容性
- Toast 不要用第三方库，用 SwiftUI overlay + transition 即可
- haptic 需要 import UIKit
- 时间格式用 DateFormatter 或 RelativeDateTimeFormatter
