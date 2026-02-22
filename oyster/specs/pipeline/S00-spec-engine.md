---
task_id: S00-spec-engine
project: pipeline
priority: 0
depends_on: []
modifies: ["dispatch/pipeline/spec_engine.py"]
executor: glm
---

## 目标
创建 Spec 质量引擎 — 不只检查 spec 质量，还能用 LLM 思考后自动增强 spec 到生产级。

## 约束
- 只创建一个文件: spec_engine.py
- 用 MiniMax API 做 spec 增强（免费无限）
- 调用方式: `mm "提示词"` CLI (已部署在 ~/Downloads/dispatch/mm)
- 不依赖任何外部 Python 库（除 PyYAML）
- 不修改任何已有文件

## 具体改动

### dispatch/pipeline/spec_engine.py

一个 Python CLI 程序，四个命令:

```
python3 spec_engine.py validate <spec_file>       # 检查质量，打分
python3 spec_engine.py validate-all <specs_dir>    # 批量检查
python3 spec_engine.py enhance <spec_file>         # LLM 思考增强
python3 spec_engine.py enhance-all <specs_dir>     # 批量增强
python3 spec_engine.py gate <specs_dir>            # 质量门禁: 全部 >=80 分才通过
```

#### 核心逻辑

**Part 1: 质量打分器 (validate)**

满分 100 分，按维度扣分:

```python
RULES = {
    # === Front-matter (30 分) ===
    "FM_TASK_ID":     {"weight": 5,  "check": "task_id 存在且格式正确 (S01-xxx)"},
    "FM_PROJECT":     {"weight": 3,  "check": "project 存在"},
    "FM_PRIORITY":    {"weight": 3,  "check": "priority 存在且为 0-3"},
    "FM_DEPENDS":     {"weight": 3,  "check": "depends_on 是 list"},
    "FM_MODIFIES":    {"weight": 8,  "check": "modifies 是 list 且不为空，每个路径格式正确"},
    "FM_EXECUTOR":    {"weight": 3,  "check": "executor 是 glm/codex"},
    "FM_NO_CONFLICT": {"weight": 5,  "check": "modifies 的文件不与同目录其他 spec 冲突"},

    # === Body 结构 (30 分) ===
    "BODY_GOAL":       {"weight": 8,  "check": "有 ## 目标，且 > 20 字"},
    "BODY_CONSTRAINT": {"weight": 5,  "check": "有 ## 约束"},
    "BODY_CHANGES":    {"weight": 7,  "check": "有 ## 具体改动 或代码示例"},
    "BODY_ACCEPT":     {"weight": 7,  "check": "有 ## 验收标准，>=2 个 checkbox"},
    "BODY_DONOT":      {"weight": 3,  "check": "有 ## 不要做"},

    # === 代码质量 (20 分) ===
    "CODE_EXAMPLE":    {"weight": 8,  "check": "有 ```python 或 ```bash 代码块"},
    "CODE_KWARGS":     {"weight": 4,  "check": "函数定义用 kwargs 不用位置参数"},
    "CODE_NO_SECRET":  {"weight": 5,  "check": "无硬编码密钥/密码"},
    "CODE_ENV_VAR":    {"weight": 3,  "check": "用 os.environ 不用硬编码 URL"},

    # === 安全与测试 (20 分) ===
    "SEC_NO_ENV":      {"weight": 3,  "check": "不提交 .env"},
    "SEC_VALIDATE":    {"weight": 5,  "check": "有验证命令 (pytest/curl/npm test)"},
    "SEC_BYZANTINE":   {"weight": 5,  "check": "API spec 包含异常场景测试"},
    "SEC_UI_GUARD":    {"weight": 4,  "check": "改后端的 spec 有'不动 UI/CSS'约束"},
    "SEC_PYDANTIC":    {"weight": 3,  "check": "涉及 Pydantic 的有大小写约束"},
}
```

每个规则返回 PASS/FAIL，FAIL 扣对应 weight 分。

**Part 2: LLM 增强器 (enhance)**

思考流程:
1. 读取原始 spec
2. 跑 validate 得到缺失项
3. 读取项目代码上下文 (modifies 指向的文件前 50 行)
4. 构造增强 prompt，让 MiniMax 补全:
   - 补 "## 约束" 段
   - 补 "## 不要做" 段
   - 补充验收标准 checkbox
   - 补充代码示例 (基于真实代码上下文)
   - 补充安全检查项
   - 补充拜占庭测试场景 (如果是 API)
5. 合并增强内容到原始 spec（不删除已有内容，只添加）
6. 再跑一次 validate 验证分数提升
7. 写回文件（备份原始为 .bak）

增强 prompt 模板:
```
你是 Spec 质量增强器。根据以下信息补全 spec:

原始 Spec:
{spec_content}

缺失检查项:
{failed_rules}

项目代码上下文:
{code_context}

SOP 要求:
1. 验收标准必须用 - [ ] 格式，至少 3 个
2. 必须有 ## 约束 段，包含: 不动 UI/CSS, kwargs only, 不硬编码 secret
3. 必须有 ## 不要做 段
4. 如果涉及 API，验收标准必须包含: 空输入测试, 超时测试, 无效 token 测试
5. 代码示例必须基于真实代码上下文，不能是伪代码
6. 函数定义必须用 kwargs

输出: 增强后的完整 spec (保留原始内容，补充缺失部分)
```

调用方式:
```python
import subprocess
result = subprocess.run(
    ["python3", str(MM_CLI), prompt],
    capture_output=True, text=True, timeout=120
)
enhanced_content = result.stdout
```

**Part 3: 质量门禁 (gate)**

```python
def gate(specs_dir):
    reports = validate_all(specs_dir)
    min_score = min(r.score for r in reports)
    avg_score = sum(r.score for r in reports) / len(reports)

    if min_score < 60:
        print(f"BLOCKED: 最低分 {min_score} < 60，必须 enhance 后重试")
        sys.exit(2)
    elif avg_score < 80:
        print(f"WARNING: 平均分 {avg_score:.0f} < 80，建议 enhance")
        sys.exit(1)
    else:
        print(f"PASSED: 最低 {min_score}, 平均 {avg_score:.0f}")
        sys.exit(0)
```

#### 输出格式

validate 输出:
```
📊 S01-db-and-config.md — 85/100
  ✅ FM_TASK_ID (5/5)
  ✅ FM_PROJECT (3/3)
  ❌ BODY_CONSTRAINT (0/5) — 缺少 ## 约束 段
  ❌ SEC_BYZANTINE (0/5) — API spec 缺少异常场景测试
  → 建议: python3 spec_engine.py enhance S01-db-and-config.md
```

enhance 输出:
```
🔧 增强 S01-db-and-config.md
  原始分数: 65/100
  缺失项: BODY_CONSTRAINT, BODY_DONOT, SEC_BYZANTINE
  读取代码上下文: db.py (50 行), config.py (50 行)
  调用 MiniMax 增强...
  增强后分数: 92/100 (+27)
  已写回: specs/pipeline/S01-db-and-config.md
  备份: specs/pipeline/S01-db-and-config.md.bak
```

gate 输出:
```
🚦 质量门禁: specs/pipeline/
  S00: 95/100 ✅
  S01: 92/100 ✅
  S02: 88/100 ✅
  ...
  最低: 85 | 平均: 91 | 状态: PASSED ✅
```

## 验收标准
- [ ] `python3 spec_engine.py validate specs/pipeline/S01-db-and-config.md` 输出分数和各规则结果
- [ ] `python3 spec_engine.py validate-all specs/pipeline/` 批量检查 9 个 spec
- [ ] `python3 spec_engine.py enhance specs/pipeline/S01-db-and-config.md` 调用 mm CLI 增强后分数提升
- [ ] `python3 spec_engine.py gate specs/pipeline/` 最低分 < 60 返回退出码 2
- [ ] 增强后原始文件有 .bak 备份
- [ ] 无硬编码密钥检测能工作
- [ ] modifies 冲突检测能工作 (同目录两个 spec 改同一文件)

## 不要做
- 不要修改任何 spec 文件（validate 只读，enhance 写之前备份）
- 不要修改 dispatch/ 下已有文件
- 不要安装新的 Python 包（只用标准库 + PyYAML）
- 不要把 MiniMax API key 硬编码（mm CLI 自己读 ~/.oyster-keys/minimax.env）
