#!/usr/bin/env python3
"""Generate and install launchd agents for dispatch projects."""

import os
import sys
import subprocess
from pathlib import Path

DISPATCH_PATH = os.path.expanduser("~/Downloads/dispatch")
TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dispatch.{project}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{dispatch_path}/dispatch.py</string>
        <string>start</string>
        <string>{project}</string>
        <string>--watch</string>
        <string>--daemon</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{dispatch_path}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>SuccessfulExit</key>
    <false/>
    
    <key>StandardOutPath</key>
    <string>/tmp/dispatch-{project}.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/dispatch-{project}.err.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
"""

LAUNCHAGENTS_DIR = Path(os.path.expanduser("~/Library/LaunchAgents"))


def generate_plist(project: str) -> str:
    return TEMPLATE.format(dispatch_path=DISPATCH_PATH, project=project)


def install_agent(project: str):
    plist_content = generate_plist(project)
    plist_path = LAUNCHAGENTS_DIR / f"com.dispatch.{project}.plist"

    # Create LaunchAgents dir if not exists
    LAUNCHAGENTS_DIR.mkdir(parents=True, exist_ok=True)

    # Write plist
    with open(plist_path, "w") as f:
        f.write(plist_content)

    print(f"Generated: {plist_path}")

    # Load the agent
    result = subprocess.run(
        ["launchctl", "load", str(plist_path)], capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Loaded: com.dispatch.{project}")
    else:
        print(f"Load warning: {result.stderr}")


def uninstall_agent(project: str):
    plist_path = LAUNCHAGENTS_DIR / f"com.dispatch.{project}.plist"
    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
        plist_path.unlink()
        print(f"Uninstalled: com.dispatch.{project}")


def list_agents():
    result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if "dispatch" in line:
            print(line)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  dispatchd.py install <project>   # Install and start agent")
        print("  dispatchd.py uninstall <project> # Stop and remove agent")
        print("  dispatchd.py list               # List running agents")
        print("  dispatchd.py install-all       # Install all known projects")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "install" and len(sys.argv) == 3:
        install_agent(sys.argv[2])
    elif cmd == "uninstall" and len(sys.argv) == 3:
        uninstall_agent(sys.argv[2])
    elif cmd == "list":
        list_agents()
    elif cmd == "install-all":
        projects = [
            "infrastructure",
            "clawphones-admin",
            "clawphones",
            "clawphones-backend",
            "gem-platform",
            "clawmarketing",
        ]
        for p in projects:
            install_agent(p)
    else:
        print(f"Unknown command: {cmd}")
