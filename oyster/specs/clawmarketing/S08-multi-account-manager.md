---
task_id: S08-multi-account-manager
project: clawmarketing
priority: 1
depends_on: []
modifies:
  - backend/services/multi_account_manager.py
---

## 目标

实现 Multi-Account Manager，管理 50+ 账号。

## 约束

- **不动 UI/CSS**

## 具体改动

### MultiAccountManager

```python
class MultiAccountManager:
    """Handle 50+ accounts with identity separation"""
    
    async def add_account(self, handle: str, app_password: str, persona_id: int = None):
        """Add new account"""
        
    async def remove_account(self, account_id: int):
        """Remove account"""
        
    async def get_account(self, account_id: int) -> dict:
        """Get account details"""
        
    async def list_accounts(self, filter: dict = None) -> list[dict]:
        """List all accounts with filters"""
        
    async def bulk_operation(self, account_ids: list[int], operation: str):
        """Bulk operations: enable, disable, pause"""
        
    async def get_account_health(self, account_id: int) -> dict:
        """Get account health status"""
```

### 功能

- 账号注册/移除
- 身份隔离 (不同 persona)
- 批量操作
- 账号健康状态
- per-account rate limits

## 验收标准

- [ ] 能添加/移除账号
- [ ] 能列出账号
- [ ] 能批量操作
- [ ] 有健康检查

## 不要做

- ❌ 不改 UI
