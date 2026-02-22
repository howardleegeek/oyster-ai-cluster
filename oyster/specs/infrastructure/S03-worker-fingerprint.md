---
task_id: S03-infra-worker-fingerprint
project: infrastructure
priority: 1
depends_on: []
modifies:
  - dispatch/worker_fingerprint.py
executor: glm
---

## 目标
创建 worker fingerprint 脚本，自动检测节点环境信息

## 具体改动

### 创建文件: dispatch/worker_fingerprint.py

```python
#!/usr/bin/env python3
"""Worker fingerprint - detect and report node environment"""
import json
import subprocess
import platform
import os

def get_fingerprint():
    """Detect worker environment fingerprint"""
    fp = {
        "hostname": platform.node(),
        "os": platform.system() + " " + platform.release(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": os.sys.executable,
    }
    
    # Detect tools
    tools = ["node", "npm", "git", "docker", "pnpm"]
    fp["tools"] = {}
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
            fp["tools"][tool] = result.stdout.strip() or result.stderr.strip()
        except:
            fp["tools"][tool] = None
    
    # Detect Node version
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        fp["node_version"] = result.stdout.strip()
    except:
        fp["node_version"] = None
    
    return fp

if __name__ == "__main__":
    fp = get_fingerprint()
    print(json.dumps(fp, indent=2))
```

## 验收标准
- [ ] 脚本能运行 `python3 dispatch/worker_fingerprint.py`
- [ ] 输出 JSON 包含 hostname, os, arch, python_version, node_version, tools

## 测试命令
```bash
cd ~/Downloads/dispatch
python3 worker_fingerprint.py
```
