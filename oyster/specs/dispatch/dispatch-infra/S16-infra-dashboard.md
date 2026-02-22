---
task_id: S16-infra-dashboard
project: dispatch-infra
priority: 2
depends_on: ["S10-infra-guardian", "S12-code-self-audit"]
modifies:
  - dispatch/infra_dashboard.py
executor: glm
---

# Infra Dashboard: 自我迭代状态可视化

## 目标
创建一个实时 dashboard，展示 infra 自我迭代模块的状态

## 具体改动

### 1. 新增 infra_dashboard.py
```python
class InfraDashboard:
    """展示自我迭代状态的 Web Dashboard"""
    
    def get_status(self) -> dict:
        return {
            "guardian": self.get_guardian_status(),
            "predictor": self.get_predictor_status(),
            "auditor": self.get_auditor_status(),
            "cleaner": self.get_cleaner_status(),
            "evolve": self.get_evolve_status()
        }
    
    def render_html(self) -> str:
        """生成 HTML Dashboard"""
```

### 2. 端点
- GET /api/status - JSON 状态
- GET / - HTML Dashboard

### 3. 指标
- Guardian: 检查次数、修复次数、成功率
- Predictor: 预测准确度、资源利用率
- Auditor: 发现问题数、严重度分布
- Cleaner: 清理 ghost 数、释放 slots
- Evolve: 发现工具数、集成数

## 验收标准
- [ ] 能展示 5 个模块状态
- [ ] 能显示历史趋势
- [ ] 能生成 HTML 页面
