# 基础设施全面修复计划

## 一、当前问题总结

| 问题 | 严重性 | 根因 |
|------|--------|------|
| 节点代码缺失 | P0 | dispatch 不同步代码 |
| task-watcher 停止 | P0 | 无自动重启 |
| 代码不同步 | P0 | 无 rsync 机制 |
| Guardian 监控不全 | P1 | 没监控代码/watcher |
| dispatch 任务卡住 | P1 | 标记 running 但未执行 |
| Bridge 消息丢失 | P1 | 轮询间隔太长 |

## 二、架构缺陷

### 2.1 代码同步缺失
```
当前: dispatch 推 spec → 节点执行 → 失败(缺代码)
应该: dispatch 推 spec 前先 rsync 代码 → 执行
```

### 2.2 任务执行流程断裂
```
当前: DB 标记 running → 没人执行
应该: task-watcher 持续监听 → 执行 → 更新状态
```

### 2.3 监控盲区
```
当前: Guardian 只监控基础设施
应该: Guardian 监控全链路(代码同步+任务执行+watcher)
```

## 三、修复计划

### P0 - 立即修复

#### 1. 代码同步机制
- [ ] **dispatch 推任务前自动 rsync**
  - 修改 deploy_task_to_node()
  - 推送前先检查远程代码是否存在
  - 不存在则先 rsync
  
- [ ] **Guardian C6: 代码同步检查**
  - 每 30 分钟检查节点代码
  - 差异时自动 rsync
  - 记录同步日志

#### 2. task-watcher 稳定化
- [x] **自动重启循环** (已完成)
- [ ] **Guardian 监控 watcher 进程**
- [ ] **加入 launchd 开机自启**

#### 3. 任务状态一致性
- [ ] **修复 dispatch 状态同步**
  - task-watcher 执行后必须更新 DB
  - 不再依赖 wrapper 回调

### P1 - 近期修复

#### 4. Bridge 可靠性
- [ ] **缩短轮询间隔** 2s → 1s
- [ ] **消息持久化确认**
- [ ] **失败重试机制**

#### 5. Guardian 增强
- [ ] **C7: 任务执行监控**
  - 检测长期 pending 任务
  - 自动触发执行
  
- [ ] **C8: 节点健康评分**
  - 综合 CPU/内存/任务完成率
  - 自动负载均衡

#### 6. dispatch 稳定性
- [ ] **修复 dispatch 持续运行**
  - 当前 start 命令会退出
  - 应该 daemon 模式
  
- [ ] **超时机制**
  - 2 小时自动 kill 任务
  - 防止无限挂起

### P2 - 架构升级

#### 7. 混合模式完善
- [ ] **节点 pull 模式**
  - 节点主动拉取任务
  - 减少对 Mac-1 依赖
  
- [ ] **分布式调度**
  - 多节点协作
  - 自动负载均衡

#### 8. 监控告警
- [ ] **Slack/Discord 告警**
- [ ] **任务完成通知**
- [ ] **失败自动重试**

## 四、实施顺序

```
第一周:
├── 1. dispatch rsync 机制
├── 2. Guardian C6 代码同步
├── 3. task-watcher launchd

第二周:
├── 4. Bridge 可靠性
├── 5. dispatch daemon 模式
└── 6. 任务状态修复

第三周:
├── 7. Guardian C7 任务监控
├── 8. 自动告警
└── 9. 负载均衡

第四周:
└── 10. 分布式架构设计
```

## 五、关键文件清单

| 文件 | 修改内容 |
|------|----------|
| `dispatch.py` | +rsync +daemon 模式 |
| `guardian.py` | +C6 代码同步 +C7 任务监控 |
| `task-watcher.py` | +launchd 配置 |
| `bridge-daemon.py` | +可靠消息 |
| `nodes.json` | +代码路径配置 |

## 六、验证标准

- [ ] 推送任务后节点自动 rsync 代码
- [ ] watcher 停止后 30 秒内自动重启
- [ ] Guardian 5 分钟检测全链路
- [ ] Bridge 消息 5 秒内响应
- [ ] 任务状态 100% 一致
