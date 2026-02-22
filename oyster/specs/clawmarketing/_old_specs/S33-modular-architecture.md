---
task_id: S33-modular-architecture
project: clawmarketing
priority: 1
depends_on: []
modifies: []
executor: glm
---

## 目标
重构为模块化架构 - 参考 fastapi-large-app-template

## 约束
- 保持现有API兼容
- 插件式Agent系统
- 可扩展架构

## 模块化架构设计

### 1. Backend模块结构
```
backend/
├── app/                    # 主应用
│   ├── api/               # API路由 (按域划分)
│   │   ├── v1/
│   │   │   ├── auth/
│   │   │   ├── brands/
│   │   │   ├── agents/   # 可插拔Agent
│   │   │   └── ...
│   │   └── dependencies/
│   ├── core/              # 核心配置
│   ├── db/                # 数据库
│   ├── models/            # SQLModel
│   ├── schemas/           # Pydantic
│   └── services/          # 业务逻辑
├── plugins/               # 插件目录
│   ├── agents/            # Agent插件
│   │   ├── twitter/
│   │   ├── discord/
│   │   ├── bluesky/
│   │   └── scout/
│   └── middleware/        # 可插拔中间件
└── tests/
```

### 2. Agent插件接口
```python
class BaseAgent(Protocol):
    name: str
    async def post(self, content: str) -> AgentResponse: ...
    async def schedule(self, content: str, time: datetime) -> AgentResponse: ...
    async def get_status(self, post_id: str) -> AgentStatus: ...

# 动态加载
def get_agent(platform: str) -> BaseAgent:
    agents = {
        "twitter": TwitterAgent,
        "discord": DiscordAgent,
        "bluesky": BlueskyAgent,
    }
    return agents[platform]()
```

### 3. 前端模块
```
frontend/
├── components/
│   ├── ui/               # shadcn/ui 基础组件
│   ├── agents/            # Agent特定组件
│   └── features/         # 功能组件
├── app/                  # Next.js 15 App Router
├── lib/                  # 工具函数
└── hooks/               # 自定义Hooks
```

### 4. 插件注册系统
```python
# plugins/registry.py
class PluginRegistry:
    _agents: dict = {}
    _middlewares: list = {}
    
    @classmethod
    def register_agent(cls, name: str, agent_class):
        cls._agents[name] = agent_class
        
    @classmethod
    def get_agent(cls, name: str):
        return cls._agents.get(name)
```

## 具体改动
1. 重构 backend/ 为 app/ 结构
2. 创建 plugins/agents/ 目录
3. 实现 BaseAgent 协议
4. 创建 PluginRegistry
5. 更新 main.py 使用插件注册

##验收标准
- [ ] Agent可动态加载
- [ ] 新Agent只需添加文件
- [ ] 中间件可插拔
- [ ] 保持现有功能
