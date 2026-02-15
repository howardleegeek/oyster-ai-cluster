#!/usr/bin/env python3
"""
Browser Bridge - 集成已有 browsermcp_api.py

功能:
- 连接本地浏览器 MCP Bridge
- 提供简单 API 给 Slot Agent
- 视觉验证能力
"""

import os
import sys
from pathlib import Path

# 添加路径
sys.path.insert(
    0, str(Path(__file__).parent.parent / "New Code" / "oyster-autonomous-agents")
)

try:
    from browsermcp_api import (
        bridge_health,
        bridge_tools,
        call_tool,
        run_script,
        BrowserMCPError,
    )

    BROWSER_MCP_AVAILABLE = True
except ImportError:
    BROWSER_MCP_AVAILABLE = False

from typing import Optional, Dict, Any, List
from datetime import datetime


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [BrowserBridge] {msg}", flush=True)


class BrowserBridge:
    """浏览器桥接 - 使用已有 browsermcp_api.py"""

    def __init__(self, bridge_base: str = None):
        self.bridge_base = bridge_base or os.getenv(
            "OYSTER_BROWSERMCP_BRIDGE_BASE", "http://127.0.0.1:7333"
        )
        self.available = False
        self.tools = []

        if BROWSER_MCP_AVAILABLE:
            self.check_health()

    def check_health(self) -> bool:
        """检查浏览器桥接是否可用"""
        try:
            health = bridge_health(self.bridge_base, timeout=2.0)
            self.available = health.get("ok", False)
            if self.available:
                self.tools = bridge_tools(self.bridge_base)
                log(f"Browser bridge available: {len(self.tools)} tools")
            return self.available
        except Exception as e:
            log(f"Bridge not available: {e}")
            self.available = False
            return False

    def navigate(self, url: str) -> Dict:
        """导航到 URL"""
        ok, result, err = call_tool(
            "browser_navigate", {"url": url}, base=self.bridge_base
        )
        return {"ok": ok, "result": result, "error": err}

    def snapshot(self) -> str:
        """获取页面快照"""
        ok, result, err = call_tool("browser_snapshot", {}, base=self.bridge_base)
        if ok:
            return result.get("content", [{"text": ""}])[0].get("text", "")
        return f"Error: {err}"

    def screenshot(self) -> Optional[bytes]:
        """获取截图 (base64)"""
        ok, result, err = call_tool("browser_screenshot", {}, base=self.bridge_base)
        if ok:
            import base64

            data = result.get("content", [{}])[0].get("source", "")
            return base64.b64decode(data)
        return None

    def click(self, selector: str) -> bool:
        """点击元素"""
        ok, result, err = call_tool(
            "browser_click", {"selector": selector}, base=self.bridge_base
        )
        return ok

    def type(self, selector: str, text: str) -> bool:
        """输入文本"""
        ok, result, err = call_tool(
            "browser_type", {"selector": selector, "text": text}, base=self.bridge_base
        )
        return ok

    def wait(self, seconds: float) -> bool:
        """等待"""
        ok, result, err = call_tool(
            "browser_wait", {"time": seconds}, base=self.bridge_base
        )
        return ok

    def errors(self) -> List[str]:
        """获取 JS 错误"""
        ok, result, err = call_tool("browser_errors", {}, base=self.bridge_base)
        if ok:
            return result.get("content", [{}])[0].get("text", "").split("\n")
        return []

    def console(self) -> List[Dict]:
        """获取 console 日志"""
        ok, result, err = call_tool("browser_console", {}, base=self.bridge_base)
        if ok:
            return result.get("content", [])
        return []

    def evaluate(self, script: str) -> Any:
        """执行 JavaScript"""
        ok, result, err = call_tool(
            "browser_evaluate", {"script": script}, base=self.bridge_base
        )
        if ok:
            return result
        return {"error": err}

    def validate_no_errors(self) -> bool:
        """验证页面无 JS 错误"""
        errors = self.errors()
        if errors:
            log(f"Found {len(errors)} JS errors")
            return False
        return True

    def validate_element_exists(self, selector: str) -> bool:
        """验证元素存在"""
        script = f"document.querySelector('{selector}') !== null"
        result = self.evaluate(script)
        return result.get("result", False)

    def validate_text_visible(self, text: str) -> bool:
        """验证文本可见"""
        script = f"""
            (function() {{
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                while(walker.nextNode()) {{
                    if(walker.currentNode.textContent.includes('{text}')) return true;
                }}
                return false;
            }})()
        """
        result = self.evaluate(script)
        return result.get("result", False)

    def run_e2e_steps(self, steps: List[Dict]) -> Dict:
        """运行 E2E 步骤"""
        return run_script(steps, base=self.bridge_base)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Browser Bridge")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--navigate", metavar="URL")
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--screenshot", action="store_true")
    parser.add_argument("--click", metavar="SELECTOR")
    parser.add_argument("--type", nargs=2, metavar=("SELECTOR", "TEXT"))
    parser.add_argument("--errors", action="store_true")
    parser.add_argument("--validate-errors", action="store_true")

    args = parser.parse_args()

    browser = BrowserBridge()

    if args.health:
        print(f"Available: {browser.available}")
        print(f"Tools: {len(browser.tools)}")

    if args.navigate:
        result = browser.navigate(args.navigate)
        print(f"Navigate: {result}")

    if args.snapshot:
        snapshot = browser.snapshot()
        print(f"Snapshot: {snapshot[:500]}...")

    if args.screenshot:
        img = browser.screenshot()
        if img:
            print(f"Screenshot: {len(img)} bytes")
        else:
            print("Screenshot failed")

    if args.click:
        ok = browser.click(args.click)
        print(f"Click: {ok}")

    if args.type:
        selector, text = args.type
        ok = browser.type(selector, text)
        print(f"Type: {ok}")

    if args.errors:
        errors = browser.errors()
        print(f"Errors: {errors}")

    if args.validate_errors:
        ok = browser.validate_no_errors()
        print(f"Validate: {ok}")


if __name__ == "__main__":
    main()
