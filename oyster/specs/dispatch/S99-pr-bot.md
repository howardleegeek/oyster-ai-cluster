---
executor: glm
task_id: S99-pr-bot
project: dispatch
priority: 2
depends_on: [S99-code-pipeline-core, S99-code-quality-gate]
modifies:
  - pipeline/pr_bot.py
  - dispatch.py
---
executor: glm

## 目标
实现 PR Bot：自动创建 PR + CI 检查 + 必要时 rerun。

## 约束
- 复用 CDP/VisionAgent 检查 CI 状态
- 高风险文件(auth/payment)自动标记 needs_human
- PR 描述自动生成 CHANGELOG

## 具体改动

### pipeline/pr_bot.py (新文件)
```python
class PRBot:
    """自动 PR 管理"""
    
    def create_pr(self, repo: str, branch: str, title: str, body: str) -> str:
        """创建 PR，返回 PR URL"""
    
    def check_ci_status(self, pr_url: str) -> CIStatus:
        """检查 CI 状态"""
    
    def wait_for_ci(self, pr_url: str, timeout: int = 600) -> CIStatus:
        """等待 CI 完成"""
    
    def rerun_workflow(self, pr_url: str, workflow: str):
        """重新运行 workflow"""
    
    def add_comment(self, pr_url: str, comment: str):
        """添加评论"""
    
    def is_high_risk(self, changes: list) -> bool:
        """判断是否高风险改动"""
```

### dispatch.py 扩展
- 新增 `pr-bot` 子命令

## 验收标准
- [ ] 可创建 PR
- [ ] 可检查 CI 状态
- [ ] 高风险文件自动标记

## 验证命令
```bash
cd ~/Downloads/dispatch && python3 -c "
from pipeline.pr_bot import PRBot
bot = PRBot()
# test basic init
print('PRBot initialized')
"
```
