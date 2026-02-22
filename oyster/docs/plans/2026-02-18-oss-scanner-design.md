# OSS Scanner Design — factory_daemon 开源扫描模块

> Date: 2026-02-18
> Status: Approved
> Approach: 方案 A (GitHub REST API, 独立模块, feature flag)

---

## 问题

factory_daemon 目前的 spec 生成是从零写代码。v6 要求 OSS-First：先搜 GitHub 有没有合适的开源项目，有就 fork，spec 基于 fork 代码写。

## 设计

### 新文件: `pipeline/oss_scanner.py`

独立模块，不改 factory_daemon 核心逻辑。factory_daemon 通过 feature flag 调用。

### 流程

```
auto_research() → directions
        ↓
oss_scan_directions(directions)     ← NEW
  ├─ search_github_oss(keywords)    ← GitHub Search API
  ├─ score_and_decide(candidates)   ← 自动评分: fork / fork_modify / self_build
  ├─ fork_repo(repo_url)            ← gh repo fork --clone
  └─ analyze_repo_structure(path)   ← tree + README + entry points
        ↓
directions (enriched with oss_candidates + fork_path + repo_structure)
        ↓
generate_research_specs(directions) ← spec 模板根据有无 fork 不同
```

### 函数签名

```python
def search_github_oss(keywords: list[str], limit: int = 5) -> list[dict]:
    """Search GitHub REST API, return top repos sorted by stars.
    Returns: [{repo, stars, license, updated, description, language, url}]
    """

def score_and_decide(candidates: list[dict], direction: str) -> dict:
    """Score candidates and decide: fork / fork_modify / self_build.
    Rules:
      - Stars > 5K + MIT/Apache + updated < 6 months → fork
      - Stars > 1K + partial match → fork_modify
      - else → self_build
    Returns: {decision, repo_url, repo_name, reason}
    """

def fork_repo(repo_url: str, project_name: str) -> str | None:
    """Fork repo to howardleegeek org and clone locally.
    Returns: local path or None on failure
    """

def analyze_repo_structure(repo_path: str) -> dict:
    """Analyze forked repo structure for spec generation.
    Returns: {tree, readme_summary, entry_points, test_dir, language, key_files}
    """

def oss_scan_directions(directions: list[dict]) -> list[dict]:
    """Main entry: enrich directions with OSS scan results.
    For each direction: search → score → fork if needed → analyze → enrich
    """
```

### Spec 模板变化

有 fork:
```markdown
## 代码基础
Fork from: {repo_url} ({stars} stars, {license})
本地路径: {fork_path}
目录结构:
{tree_output}
入口文件: {entry_points}
测试目录: {test_dir}

## 约束
- 不改原有功能，只加新功能
- 复用现有测试框架
- 遵循原项目代码风格
```

无 fork (self_build):
```markdown
## 约束
- 从零实现 (无合适开源方案)
- （跟现在一样）
```

### factory_daemon 改动 (最小)

```python
# 新增 import
from pipeline.oss_scanner import oss_scan_directions, OSS_SCAN_ENABLED

# run_factory_cycle() Phase 2 改动:
if directions:
    if OSS_SCAN_ENABLED:
        directions = oss_scan_directions(directions)  # enrich
    specs = generate_research_specs(directions)
```

### 安全措施

1. `OSS_SCAN_ENABLED = False` 默认关闭
2. `oss_scanner.py --test` 可独立运行测试
3. 所有 GitHub API 调用有 try/except，失败不影响现有流程
4. fork 操作用 `--clone=false` 先不 clone，决定后再 clone
5. 扫描报告写到 `open-source-atlas/projects/` 供人工 review

### Rate Limits

- GitHub Search API: 30 req/min (authenticated)
- factory_daemon 每小时 research 一次，每次 ~16 个方向
- 每个方向搜 1-2 次 = ~32 req/hour，远低于限制
