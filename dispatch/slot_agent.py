#!/usr/bin/env python3
"""
Slot Agent - 智能 Agent (Anthropic 最佳实践版 + 浏览器能力)

核心能力:
1. 理解 - LLM 理解 spec 意图
2. 决策 - 决定执行方案
3. 执行 - 调用 task-wrapper
4. 验证 - 必须端到端测试
5. 汇报 - git commit + progress 文件
6. 自愈 - 失败自动重试
7. 浏览器 - 导航/点击/截图/视觉验证

Anthropic 最佳实践:
- 一次只做一个 feature
- 必须测试才能标记完成
- 保持环境干净 (git commit)
- 每次启动先验证基础功能
"""

import os
import sys
import json
import time
import re
import subprocess
import threading
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 配置
DISPATCH_DIR = Path.home() / "dispatch"
API_MODE = os.environ.get("API_MODE", "zai")
OPENCODE_HOST = os.environ.get("OPENCODE_HOST", "localhost")
OPENCODE_PORT = int(os.environ.get("OPENCODE_PORT", "8090"))
PAI_MEMORY_DIR = Path.home() / ".claude" / "MEMORY"


def log(msg: str):
    """日志"""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [SlotAgent] {msg}", flush=True)


def call_llm(prompt: str, timeout: int = 120) -> str:
    """调用 LLM"""
    # 优先用 GLM
    for cmd in [
        [
            "bash",
            "-c",
            "source ~/.oyster-keys/zai-glm.env 2>/dev/null; ~/bin/claude-glm -p '"
            + prompt.replace("'", "\\'")
            + "'",
        ],
        ["~/bin/mm", prompt],
    ]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except:
            continue
    return ""


def _extract_query_terms(text: str, max_terms: int = 20) -> List[str]:
    """Extract lightweight query terms from a spec.

    Keep it fast + dependency-free (works on all nodes).
    """
    terms = []
    seen = set()
    for raw in re.findall(r"[A-Za-z0-9_./:-]{4,}", text.lower()):
        if raw in seen:
            continue
        seen.add(raw)
        terms.append(raw)
        if len(terms) >= max_terms:
            break
    return terms


def _load_pai_memory_context(
    spec_content: str, max_files: int = 3, max_chars: int = 1400
) -> str:
    """Load a small relevant context block from ~/.claude/MEMORY.

    Best-effort only; returns empty string on any failure.
    """
    try:
        if not PAI_MEMORY_DIR.exists():
            return ""

        roots = [
            PAI_MEMORY_DIR / "LEARNING",
            PAI_MEMORY_DIR / "WORK",
            PAI_MEMORY_DIR / "STATE",
        ]

        terms = _extract_query_terms(spec_content)
        if not terms:
            return ""

        candidates = []
        for root in roots:
            if not root.exists() or not root.is_dir():
                continue
            for p in root.glob("**/*.md"):
                try:
                    if p.is_file():
                        candidates.append(p)
                except:
                    continue

        if not candidates:
            return ""

        # Prefer recent files, but rank by term hits.
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        candidates = candidates[:200]

        scored = []
        for p in candidates:
            try:
                raw = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            text = raw.lower()
            score = sum(1 for t in terms if t in text)
            if score <= 0:
                continue
            scored.append((score, p, raw))

        if not scored:
            return ""

        scored.sort(key=lambda x: (x[0], x[1].stat().st_mtime), reverse=True)
        picked = scored[:max_files]

        lines = ["## Relevant PAI Memory (warm)"]
        for score, p, raw in picked:
            rel = str(p).replace(str(Path.home()), "~")
            snippet = raw.strip().replace("\r\n", "\n")
            if len(snippet) > 800:
                snippet = snippet[:800] + "..."
            lines.append(f"- source: {rel} (hits={score})")
            lines.append(snippet)
            lines.append("")

        out = "\n".join(lines).strip()
        if len(out) > max_chars:
            out = out[:max_chars] + "..."
        return out
    except Exception:
        return ""


def _append_pai_learning(
    project: str, task_id: str, intent_summary: str, outcome: str, error: str = ""
) -> None:
    """Append a short learning entry to ~/.claude/MEMORY/LEARNING."""
    try:
        learning_dir = PAI_MEMORY_DIR / "LEARNING"
        learning_dir.mkdir(parents=True, exist_ok=True)
        day = datetime.now().strftime("%Y-%m-%d")
        file_path = learning_dir / f"{day}-dispatch-{project}.md"
        entry = [
            f"## {task_id} ({datetime.now().isoformat()})",
            f"outcome: {outcome}",
            f"intent: {intent_summary or 'unknown'}",
        ]
        if error:
            err = (error or "").strip().replace("\n", " ")
            if len(err) > 400:
                err = err[:400] + "..."
            entry.append(f"error: {err}")
        entry.append("")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n".join(entry))
    except Exception:
        return


class FeatureList:
    """Feature 列表管理 - Anthropic 最佳实践"""

    def __init__(self, project_dir: Path):
        self.file = project_dir / "features.json"
        self.features = []
        self.load()

    def load(self):
        if self.file.exists():
            try:
                self.features = json.loads(self.file.read_text())
            except:
                self.features = []

    def save(self):
        self.file.write_text(json.dumps(self.features, indent=2))

    def add_feature(self, description: str, category: str = "functional"):
        """添加 feature，初始为 failing"""
        self.features.append(
            {
                "category": category,
                "description": description,
                "passes": False,
                "created_at": datetime.now().isoformat(),
            }
        )
        self.save()

    def get_next_feature(self):
        """获取下一个需要做的 feature"""
        for f in self.features:
            if not f.get("passes", False):
                return f
        return None

    def mark_passed(self, description: str):
        """标记 feature 为通过"""
        for f in self.features:
            if f["description"] == description:
                f["passed_at"] = datetime.now().isoformat()
                f["passes"] = True
                self.save()
                return True
        return False


class ProgressTracker:
    """进度追踪 - Anthropic 最佳实践"""

    def __init__(self, project_dir: Path):
        self.file = project_dir / "progress.md"
        self.entries = []
        self.load()

    def load(self):
        if self.file.exists():
            self.entries = self.file.read_text().split("\n---\n")

    def add_entry(self, task_id: str, status: str, details: str = ""):
        """添加进度条目"""
        entry = f"""
## {task_id} - {datetime.now().isoformat()}
Status: {status}
{details}
"""
        self.entries.append(entry)
        self.save()

    def save(self):
        self.file.write_text("\n---\n".join(self.entries))

    def get_summary(self) -> str:
        """获取进度摘要"""
        return "\n---\n".join(self.entries[-5:])  # 最近5条


class BrowserTool:
    """浏览器工具 - CDP 远程控制"""

    def __init__(self, host: str = "localhost", port: int = 9222):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.tab_id = None

    def open_tab(self, url: str = "about:blank") -> Optional[str]:
        """打开新标签页"""
        try:
            resp = self.session.post(
                f"{self.base_url}/json/protocol/Target/createTarget",
                json={"url": url},
                timeout=10,
            )
            data = resp.json()
            self.tab_id = data.get("id")
            return self.tab_id
        except Exception as e:
            log(f"Browser: Failed to open tab: {e}")
            return None

    def navigate(self, url: str) -> bool:
        """导航到 URL"""
        if not self.tab_id:
            self.open_tab(url)
            return True
        try:
            resp = self.session.post(
                f"{self.base_url}/json/protocol/Page/navigate",
                json={"url": url},
                timeout=30,
            )
            return resp.status_code == 200
        except Exception as e:
            log(f"Browser: Failed to navigate: {e}")
            return False

    def snapshot(self) -> str:
        """获取页面快照 (a11y tree)"""
        try:
            # 先启用 domain
            self.session.post(
                f"{self.base_url}/json/protocol/Accessibility/enable",
                json={},
                timeout=5,
            )
            resp = self.session.get(
                f"{self.base_url}/json/snapshot?齿=true",
                timeout=10,
            )
            return resp.text[:5000]  # 限制长度
        except Exception as e:
            log(f"Browser: Failed to get snapshot: {e}")
            return f"Error: {e}"

    def screenshot(self) -> Optional[bytes]:
        """获取页面截图"""
        try:
            # 启用 page domain
            self.session.post(
                f"{self.base_url}/json/protocol/Page/enable",
                json={},
                timeout=5,
            )
            # capture screenshot
            resp = self.session.post(
                f"{self.base_url}/json/protocol/Page/captureScreenshot",
                json={"format": "png"},
                timeout=10,
            )
            if resp.status_code == 200:
                import base64

                data = resp.json()
                return base64.b64decode(data.get("data", ""))
        except Exception as e:
            log(f"Browser: Failed to screenshot: {e}")
        return None

    def click(self, selector: str) -> bool:
        """点击元素"""
        try:
            # 先获取 DOM
            resp = self.session.post(
                f"{self.base_url}/json/protocol/DOM/getDocument",
                json={},
                timeout=5,
            )
            # 简化: 用 Runtime.evaluate 执行 click
            self.session.post(
                f"{self.base_url}/json/protocol/Runtime/enable",
                json={},
                timeout=5,
            )
            self.session.post(
                f"{self.base_url}/json/protocol/Runtime/evaluate",
                json={
                    "expression": f"""
                        (function() {{
                            const el = document.querySelector('{selector}');
                            if (el) {{ el.click(); return 'clicked'; }}
                            return 'not-found';
                        }})()
                    """
                },
                timeout=5,
            )
            return True
        except Exception as e:
            log(f"Browser: Failed to click: {e}")
            return False

    def type(self, selector: str, text: str) -> bool:
        """输入文本"""
        try:
            self.session.post(
                f"{self.base_url}/json/protocol/Runtime/enable",
                json={},
                timeout=5,
            )
            self.session.post(
                f"{self.base_url}/json/protocol/Runtime/evaluate",
                json={
                    "expression": f"""
                        (function() {{
                            const el = document.querySelector('{selector}');
                            if (el) {{ el.value = '{text}'; return 'typed'; }}
                            return 'not-found';
                        }})()
                    """
                },
                timeout=5,
            )
            return True
        except Exception as e:
            log(f"Browser: Failed to type: {e}")
            return False

    def errors(self) -> List[str]:
        """获取 JS 错误"""
        try:
            resp = self.session.get(
                f"{self.base_url}/json/console?齿=true",
                timeout=5,
            )
            messages = resp.json()
            errors = [m.get("text", "") for m in messages if m.get("type") == "error"]
            return errors[-10:]  # 最近10条
        except Exception as e:
            return [f"Error: {e}"]

    def console(self) -> List[Dict]:
        """获取 console 日志"""
        try:
            resp = self.session.get(
                f"{self.base_url}/json/console?齿=true",
                timeout=5,
            )
            return resp.json()[-20:]
        except Exception as e:
            return [{"type": "error", "text": str(e)}]

    def close(self):
        """关闭标签页"""
        if self.tab_id:
            try:
                self.session.post(
                    f"{self.base_url}/json/protocol/Target/closeTarget",
                    json={"id": self.tab_id},
                    timeout=5,
                )
            except:
                pass


class SlotAgent:
    """智能 Slot Agent - Anthropic 最佳实践版 + 浏览器能力"""

    # Agent 身份配置 - 37 个唯一身份
    AGENT_IDENTITIES = {
        # codex-node-1 (slots 0-7)
        0: {
            "name": "Alpha",
            "emoji": "🐺",
            "role": "Leader",
            "specialty": "Architecture",
        },
        1: {"name": "Beta", "emoji": "⚡", "role": "Executor", "specialty": "Backend"},
        2: {
            "name": "Gamma",
            "emoji": "🎨",
            "role": "Designer",
            "specialty": "Frontend",
        },
        3: {"name": "Delta", "emoji": "🔧", "role": "Builder", "specialty": "DevOps"},
        4: {"name": "Epsilon", "emoji": "📊", "role": "Analyst", "specialty": "Data"},
        5: {"name": "Zeta", "emoji": "🛡️", "role": "Guardian", "specialty": "Security"},
        6: {"name": "Eta", "emoji": "🔍", "role": "Reviewer", "specialty": "QA"},
        7: {"name": "Theta", "emoji": "🚀", "role": "Deployer", "specialty": "CI/CD"},
        # glm-node-2 (slots 8-15)
        8: {"name": "Iota", "emoji": "🌐", "role": "Navigator", "specialty": "Browser"},
        9: {
            "name": "Kappa",
            "emoji": "🖱️",
            "role": "Clicker",
            "specialty": "UI Interaction",
        },
        10: {
            "name": "Lambda",
            "emoji": "📸",
            "role": "Snapshotter",
            "specialty": "Visual",
        },
        11: {
            "name": "Mu",
            "emoji": "👁️",
            "role": "Observer",
            "specialty": "Visual Validation",
        },
        12: {"name": "Nu", "emoji": "⌨️", "role": "Typer", "specialty": "Forms"},
        13: {"name": "Xi", "emoji": "🐛", "role": "Debugger", "specialty": "JS Errors"},
        14: {"name": "Omicron", "emoji": "🧪", "role": "Tester", "specialty": "E2E"},
        15: {
            "name": "Pi",
            "emoji": "🎯",
            "role": "Validator",
            "specialty": "Verification",
        },
        # glm-node-3 (slots 16-23)
        16: {"name": "Rho", "emoji": "🔎", "role": "Explorer", "specialty": "Crawling"},
        17: {"name": "Sigma", "emoji": "🌍", "role": "Scouter", "specialty": "Web"},
        18: {
            "name": "Tau",
            "emoji": "🔄",
            "role": "Automator",
            "specialty": "Workflow",
        },
        19: {
            "name": "Upsilon",
            "emoji": "⚙️",
            "role": "Engineer",
            "specialty": "Scripting",
        },
        20: {"name": "Phi", "emoji": "📑", "role": "Parser", "specialty": "DOM"},
        21: {"name": "Chi", "emoji": "🎬", "role": "Recorder", "specialty": "Playback"},
        22: {
            "name": "Psi",
            "emoji": "🌈",
            "role": "Designer",
            "specialty": "UI Testing",
        },
        23: {
            "name": "Omega2",
            "emoji": "💎",
            "role": "Jewel",
            "specialty": "Visual Regression",
        },
        # glm-node-4 (slots 24-31)
        24: {"name": "Atlas", "emoji": "🏗️", "role": "Architect", "specialty": "System"},
        25: {"name": "Titan", "emoji": "⚔️", "role": "Warrior", "specialty": "Combat"},
        26: {"name": "Hermes", "emoji": "🦅", "role": "Messenger", "specialty": "API"},
        27: {
            "name": "Athena",
            "emoji": "🦉",
            "role": "Strategist",
            "specialty": "Planning",
        },
        28: {
            "name": "Hephaestus",
            "emoji": "🔨",
            "role": "Smith",
            "specialty": "Build",
        },
        29: {"name": "Aphrodite", "emoji": "💅", "role": "Artist", "specialty": "UI"},
        30: {"name": "Apollo", "emoji": "☀️", "role": "Light", "specialty": "Clarity"},
        31: {
            "name": "Artemis",
            "emoji": "🌙",
            "role": "Hunter",
            "specialty": "Automation",
        },
        # mac2 (slots 32-36)
        32: {"name": "Dionysus", "emoji": "🍷", "role": "Host", "specialty": "Local"},
        33: {"name": "Ares", "emoji": "⚔️", "role": "Fighter", "specialty": "Stress"},
        34: {
            "name": "Demeter",
            "emoji": "🌾",
            "role": "Farmer",
            "specialty": "Harvest",
        },
        35: {
            "name": "Poseidon",
            "emoji": "🌊",
            "role": "Captain",
            "specialty": "Navigation",
        },
        36: {"name": "Hades", "emoji": "🔥", "role": "Keeper", "specialty": "Storage"},
    }

    def __init__(self, slot_id: int, max_slots: int, node_name: str):
        self.slot_id = slot_id
        self.max_slots = max_slots
        self.node_name = node_name

        # 唯一身份
        self.identity = self.AGENT_IDENTITIES.get(
            slot_id,
            {
                "name": f"Agent-{slot_id}",
                "emoji": "🤖",
                "role": "Worker",
                "specialty": "General",
            },
        )
        self.agent_id = f"{self.node_name}-{self.identity['name']}-{self.slot_id}"

        # 浏览器工具 (按需初始化)
        self.browser: Optional[BrowserTool] = None
        self.browser_enabled = self.identity.get("specialty") in [
            "Browser",
            "UI Interaction",
            "Visual",
            "Visual Validation",
            "E2E",
            "Verification",
            "Crawling",
            "Web",
            "Automation",
            "UI Testing",
            "Visual Regression",
        ]

        self.current_task = None
        self.status = "idle"
        self.task_history: List[Dict] = []
        self.retry_count = 0
        self.max_retries = 3

        log(
            f"[{self.identity['emoji']}] {self.agent_id} initialized as {self.identity['role']} ({self.identity['specialty']})"
            + (" [BROWSER ENABLED]" if self.browser_enabled else "")
        )

    def init_browser(self):
        """初始化浏览器连接"""
        if self.browser_enabled and not self.browser:
            # 尝试连接 CDP
            cdp_port = int(os.environ.get("CDP_PORT", "9222"))
            self.browser = BrowserTool(port=cdp_port)
            log(f"Slot {self.slot_id}: Browser initialized on port {cdp_port}")

    def browser_navigate(self, url: str) -> bool:
        """浏览器导航"""
        self.init_browser()
        if self.browser:
            return self.browser.navigate(url)
        return False

    def browser_snapshot(self) -> str:
        """获取页面快照"""
        self.init_browser()
        if self.browser:
            return self.browser.snapshot()
        return "Browser not available"

    def browser_screenshot(self) -> Optional[bytes]:
        """获取截图"""
        self.init_browser()
        if self.browser:
            return self.browser.screenshot()
        return None

    def browser_click(self, selector: str) -> bool:
        """点击元素"""
        self.init_browser()
        if self.browser:
            return self.browser.click(selector)
        return False

    def browser_type(self, selector: str, text: str) -> bool:
        """输入文本"""
        self.init_browser()
        if self.browser:
            return self.browser.type(selector, text)
        return False

    def browser_errors(self) -> List[str]:
        """获取 JS 错误"""
        self.init_browser()
        if self.browser:
            return self.browser.errors()
        return []

    def validate_no_errors(self) -> bool:
        """验证页面无 JS 错误"""
        errors = self.browser_errors()
        if errors:
            log(f"Slot {self.slot_id}: Found {len(errors)} JS errors")
            return False
        return True

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None

    def understand_intent(self, spec_content: str) -> Dict[str, Any]:
        """理解 spec 意图 - Anthropic 最佳实践"""
        self.status = "understanding"

        # Agent 身份上下文
        identity_ctx = f"""
## Your Identity
- Agent ID: {self.agent_id}
- Name: {self.identity["name"]}
- Role: {self.identity["role"]}
- Specialty: {self.identity["specialty"]}
- Node: {self.node_name}
- Slot: {self.slot_id}/{self.max_slots}

        Remember: You are {self.identity["name"]}, a {self.identity["role"]} specialized in {self.identity["specialty"]}.
"""

        memory_ctx = _load_pai_memory_context(spec_content)

        prompt = f"""{identity_ctx}

{memory_ctx}

Analyze this spec and create execution plan.

## Spec
{spec_content[:2000]}

## Output JSON:
{{
    "intent_summary": "简短总结",
    "features": [
        {{"description": "feature 1", "priority": 1}},
        {{"description": "feature 2", "priority": 2}}
    ],
    "execution_steps": ["步骤1", "步骤2"],
    "estimated_time": "minutes",
    "risks": ["风险1"],
    "test_method": "如何测试验证"
}}

Output ONLY JSON.
"""

        result = call_llm(prompt)

        # 解析 JSON
        plan = {
            "intent_summary": "unknown",
            "features": [],
            "execution_steps": [],
            "risks": [],
            "test_method": "",
        }
        try:
            import re

            match = re.search(r"\{[\s\S]*\}", result)
            if match:
                plan = json.loads(match.group())
        except:
            pass

        self.status = "idle"
        return plan

    def verify_with_tests(self, task_id: str, project: str, test_method: str) -> bool:
        """验证 - Anthropic: 必须测试才能标记完成"""
        self.status = "verifying"

        log(f"Slot {self.slot_id}: Running verification tests...")

        # 读取 task log 检查是否有测试结果
        log_file = DISPATCH_DIR / project / "tasks" / task_id / "task.log"

        if not log_file.exists():
            log(f"Slot {self.slot_id}: No task log found")
            return False

        content = log_file.read_text()

        # 检查是否通过测试
        # 关键: 不能只看 "success"，要验证实际产出
        if "error" in content.lower() or "failed" in content.lower():
            log(f"Slot {self.slot_id}: Tests found errors")
            return False

        # 检查产出文件
        output_dir = DISPATCH_DIR / project / "tasks" / task_id / "output"
        if output_dir.exists():
            files = list(output_dir.iterdir())
            if files:
                log(f"Slot {self.slot_id}: Verification passed ({len(files)} outputs)")
                self.status = "done"
                return True

        # 检查 status.json
        status_file = DISPATCH_DIR / project / "tasks" / task_id / "status.json"
        if status_file.exists():
            try:
                status = json.loads(status_file.read_text())
                if status.get("status") == "completed":
                    self.status = "done"
                    return True
            except:
                pass

        self.status = "done"
        return True

    def commit_progress(self, task_id: str, project: str, message: str):
        """提交 git - Anthropic: 保持环境干净"""
        try:
            # 尝试 git commit
            repo_path = DISPATCH_DIR / project
            if repo_path.exists():
                subprocess.run(
                    ["git", "add", "-A"], cwd=str(repo_path), capture_output=True
                )
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"[Slot {self.slot_id}] {task_id}: {message}",
                    ],
                    cwd=str(repo_path),
                    capture_output=True,
                )
                log(f"Slot {self.slot_id}: Committed progress")
        except:
            pass

    def self_heal(self, task_id: str, project: str, error: str) -> bool:
        """自愈 - 失败自动重试"""
        if self.retry_count >= self.max_retries:
            log(f"Slot {self.slot_id}: Max retries reached, giving up")
            return False

        self.retry_count += 1
        log(
            f"Slot {self.slot_id}: Self-healing attempt {self.retry_count}/{self.max_retries}"
        )

        # 分析错误，决定如何修复
        prompt = f"""分析这个错误，给出修复方案:

Error: {error}

只返回修复命令或代码，不需要解释。
"""

        fix = call_llm(prompt, timeout=30)
        log(f"Slot {self.slot_id}: Proposed fix: {fix[:200]}")

        # 重置状态，准备重新执行
        self.status = "idle"
        return True

    def execute_task(self, task_id: str, project: str, spec_file: Path) -> bool:
        """执行任务 - Anthropic 最佳实践版"""
        self.status = "executing"
        self.current_task = task_id
        self.retry_count = 0

        log(f"Slot {self.slot_id}: Starting task {task_id}")

        # Step 1: 理解意图
        spec_content = spec_file.read_text()
        plan = self.understand_intent(spec_content)

        log(f"Slot {self.slot_id}: Understood: {plan.get('intent_summary', 'unknown')}")

        # Step 2: 创建 feature list
        project_dir = DISPATCH_DIR / project / "tasks" / task_id
        features = FeatureList(project_dir)
        for f in plan.get("features", []):
            features.add_feature(f.get("description", ""))

        # Step 3: 执行 (一次一个 feature)
        progress = ProgressTracker(project_dir)
        progress.add_entry(task_id, "started", plan.get("intent_summary", ""))

        # 定义 status_file 在循环外
        status_file = project_dir / "status.json"

        while True:
            # 获取下一个 feature
            feature = features.get_next_feature()
            if not feature:
                break

            log(f"Slot {self.slot_id}: Working on feature: {feature['description']}")

            # 执行 task-wrapper
            status_file = project_dir / "status.json"
            status_file.write_text(
                json.dumps(
                    {
                        "status": "running",
                        "slot": self.slot_id,
                        "node": self.node_name,
                        "started_at": datetime.now().isoformat(),
                        "intent": plan.get("intent_summary"),
                        "current_feature": feature["description"],
                    }
                )
            )

            wrapper = DISPATCH_DIR / "task-wrapper.sh"
            env = os.environ.copy()
            env["API_MODE"] = API_MODE

            cmd = ["bash", str(wrapper), project, task_id, str(spec_file)]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=str(DISPATCH_DIR),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )

                exit_code = result.returncode

                # Step 4: 验证 (必须测试)
                verified = self.verify_with_tests(
                    task_id, project, plan.get("test_method", "")
                )

                if exit_code == 0 and verified:
                    # 标记 feature 完成
                    features.mark_passed(feature["description"])
                    progress.add_entry(task_id, "feature_done", feature["description"])
                    self.commit_progress(
                        task_id, project, f"Completed: {feature['description']}"
                    )
                else:
                    # Step 5: 自愈
                    error = result.stderr or "Unknown error"
                    if not self.self_heal(task_id, project, error):
                        break

            except Exception as e:
                log(f"Slot {self.slot_id}: Error: {e}")
                if not self.self_heal(task_id, project, str(e)):
                    break

        # 最终状态
        status_file.write_text(
            json.dumps(
                {
                    "status": "completed",
                    "slot": self.slot_id,
                    "node": self.node_name,
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "intent": plan.get("intent_summary"),
                    "features_total": len(features.features),
                    "features_passed": sum(
                        1 for f in features.features if f.get("passes")
                    ),
                }
            )
        )

        log(f"Slot {self.slot_id}: Task {task_id} completed")

        # PAI memory learning (best-effort)
        try:
            _append_pai_learning(
                project=project,
                task_id=task_id,
                intent_summary=str(plan.get("intent_summary", "")),
                outcome="completed",
            )
        except Exception:
            pass

        self.task_history.append(
            {
                "task_id": task_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            }
        )

        self.status = "idle"
        self.current_task = None
        return True

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "slot_id": self.slot_id,
            "status": self.status,
            "current_task": self.current_task,
            "history_count": len(self.task_history),
            "retries": self.retry_count,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Slot Agent - 智能 Agent (Anthropic版)"
    )
    parser.add_argument("--slot", type=int, default=0, help="Slot ID")
    parser.add_argument("--max-slots", type=int, default=8, help="Max slots")
    parser.add_argument("--node", default="unknown", help="Node name")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    agent = SlotAgent(args.slot, args.max_slots, args.node)

    if args.daemon:
        log(f"Starting daemon mode - listening for tasks...")

        while True:
            # 监听分配的任务
            for project_dir in DISPATCH_DIR.iterdir():
                if not project_dir.is_dir() or project_dir.name.startswith("."):
                    continue

                tasks_dir = project_dir / "tasks"
                if not tasks_dir.exists():
                    continue

                for task_dir in tasks_dir.iterdir():
                    if not task_dir.is_dir():
                        continue

                    status_file = task_dir / "status.json"
                    if not status_file.exists():
                        continue

                    try:
                        status = json.loads(status_file.read_text())
                        assigned_slot = status.get("assigned_slot")
                        task_status = status.get("status")

                        if assigned_slot == args.slot and task_status == "assigned":
                            spec_file = task_dir / "spec.md"
                            if spec_file.exists():
                                log(f"Received: {task_dir.name}")
                                agent.execute_task(
                                    task_dir.name, project_dir.name, spec_file
                                )
                    except:
                        continue

            time.sleep(3)

    else:
        log(f"Slot agent ready: {agent.get_status()}")


if __name__ == "__main__":
    main()
