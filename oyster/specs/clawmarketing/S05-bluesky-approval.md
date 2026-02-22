---
task_id: S05-bluesky-approval
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/approval_workflow.py
---

## 目标

实现 Content Approval 工作流。

## 约束

- **不动 UI/CSS**

## 具体改动

### ApprovalWorkflow (`backend/services/approval_workflow.py`)

```python
class ApprovalWorkflow:
    """Human-in-the-loop content approval"""
    
    async def submit_for_review(self, content_item_id: int):
        """Submit content for approval"""
        pass
    
    async def approve(self, content_item_id: int, reviewer_id: int):
        """Approve content"""
        pass
    
    async def reject(self, content_item_id: int, reviewer_id: int, reason: str):
        """Reject content with reason"""
        pass
    
    async def get_pending(self, reviewer_id: int = None) -> list[dict]:
        """Get pending approvals"""
        pass
```

### ContentItem 状态扩展

```python
class ContentItem(Base):
    status = Column(String)  # draft, scheduled, pending_review, approved, published, failed, rejected
    submitted_at = Column(DateTime)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    rejection_reason = Column(String)
```

### 工作流

```
1. Writer 生成 content
2. 状态 = pending_review
3. 人工审核 (approve/reject)
4. 如果 approved → scheduled → Publisher 发布
5. 如果 rejected → Writer 收到反馈，重新生成
```

## 验收标准

- [ ] 能提交内容审核
- [ ] 能批准/拒绝内容
- [ ] 拒绝时记录原因
- [ ] 能查看待审核列表

## 不要做

- ❌ 不改 UI
