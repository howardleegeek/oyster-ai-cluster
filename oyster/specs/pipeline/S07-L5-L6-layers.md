---
task_id: S07-L5-L6-layers
project: pipeline
priority: 2
depends_on: [S02, S03, S06]
modifies: ["dispatch/pipeline/layers/L5_fix.py", "dispatch/pipeline/layers/L6_deploy.py"]
executor: glm
---

## 目标
实现 L5 修复层（读 L4 bug → 生成修复 → dispatch）和 L6 部署层（生成部署配置）

## 要创建的文件

### 1. dispatch/pipeline/layers/L5_fix.py

```python
#!/usr/bin/env python3
"""L5: 修复层 — 读 L4 bug report → 生成修复 spec → dispatch 执行"""
import json
from pathlib import Path
from layers.base import Layer, LayerResult

class L5Fix(Layer):
    name = "L5"
    max_retries = 2
    required_prev = ["L4"]

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        from executors import get_executor

        # 读 L4 bug report
        l4 = prev_results.get("L4")
        if not l4 or not l4.report:
            result.finish("FAIL", error="L4 report 缺失")
            return result

        bugs = l4.report.get("bugs", [])
        if not bugs:
            result.finish("PASS", report={"message": "无 bug，跳过", "fixes": 0})
            return result

        # 按 severity 排序 (S1 优先)
        bugs.sort(key=lambda b: b.get("severity", "S3"))

        # 生成修复 prompt
        bug_desc = []
        for i, bug in enumerate(bugs[:20]):  # 最多 20 个
            bug_desc.append(
                f"{i+1}. [{bug['severity']}] {bug['type']}: {bug['description']}\n"
                f"   详情: {bug.get('detail', 'N/A')[:200]}"
            )

        prompt = f"""你是高级工程师。修复以下项目的 bug。

项目: {project_config.name} (tech: {project_config.stack})
项目路径: {project_config.path}

Bug 列表:
{chr(10).join(bug_desc)}

要求:
1. 每个 bug 给出具体的代码修复（文件路径 + 修改内容）
2. S1 bug 必须修（崩溃/数据丢失）
3. S2 bug 尽量修（功能异常）
4. 不要改 UI/CSS
5. 不要重构不相关代码
6. 用 kwargs 不用位置参数

输出: 每个修复标明文件路径、修改前、修改后。"""

        opencode = get_executor("opencode")
        fix_result = opencode.run(prompt, cwd=project_config.path, timeout=600)

        # 写修复 spec
        specs_dir = Path(__file__).parent.parent.parent / "specs" / project_config.name
        specs_dir.mkdir(parents=True, exist_ok=True)

        spec_file = specs_dir / f"FIX-{project_config.name}-bugs.md"
        spec_content = f"""---
task_id: FIX-{project_config.name}
project: {project_config.name}
priority: 1
depends_on: []
executor: glm
---

## 目标
修复 L4 发现的 {len(bugs)} 个 bug

## Bug 列表
{chr(10).join(bug_desc)}

## AI 生成的修复方案
{fix_result.stdout if fix_result.success else '生成失败: ' + fix_result.stderr}

## 约束
- 不动 UI/CSS
- 只修 bug，不重构
- kwargs only
"""
        spec_file.write_text(spec_content)

        # dispatch 执行修复
        dispatch = get_executor("dispatch")
        dispatch_result = dispatch.start_and_wait(project_config.name)

        report = {
            "bugs_found": len(bugs),
            "s1_count": len([b for b in bugs if b["severity"] == "S1"]),
            "s2_count": len([b for b in bugs if b["severity"] == "S2"]),
            "fix_spec": str(spec_file),
            "dispatch_success": dispatch_result.success,
        }

        if dispatch_result.success:
            result.finish("PASS", report=report)
        else:
            result.finish("FAIL", report=report, error=dispatch_result.stderr[:500])

        return result
```

### 2. dispatch/pipeline/layers/L6_deploy.py

```python
#!/usr/bin/env python3
"""L6: 部署层 — 生成部署配置 + 推送"""
import json
from pathlib import Path
from layers.base import Layer, LayerResult

class L6Deploy(Layer):
    name = "L6"
    max_retries = 2
    required_prev = ["L4"]  # L4 必须 PASS

    # 部署模板
    VERCEL_JSON = {
        "buildCommand": None,
        "outputDirectory": None,
        "framework": None,
    }

    FLY_TOML = """app = "{app_name}"
primary_region = "sjc"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = {port}
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[checks]
  [checks.health]
    type = "http"
    port = {port}
    path = "{health}"
    interval = 30000
    timeout = 5000
"""

    DOCKERFILE_PYTHON = """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["{cmd}"]
"""

    ENV_EXAMPLE = """# {project} 环境变量
# 复制为 .env 并填写真实值
{vars}
"""

    def execute(self, project_config, prev_results: dict) -> LayerResult:
        result = LayerResult(layer=self.name, status="RUNNING")
        project_path = Path(project_config.path).expanduser()
        generated = []

        deploy_type = project_config.deploy

        # === .env.example ===
        if project_config.env_required:
            env_content = self.ENV_EXAMPLE.format(
                project=project_config.name,
                vars="\n".join(f"{v}=" for v in project_config.env_required),
            )
            env_file = project_path / ".env.example"
            env_file.write_text(env_content)
            generated.append(str(env_file))

        # === Vercel (静态站 / 前端) ===
        if "vercel" in deploy_type:
            vercel_config = {"version": 2}
            if project_config.frontend:
                if project_config.frontend.build:
                    vercel_config["buildCommand"] = project_config.frontend.build
                if project_config.frontend.type == "react-vite":
                    vercel_config["outputDirectory"] = "dist"
                    vercel_config["framework"] = "vite"
            vercel_file = project_path / "vercel.json"
            vercel_file.write_text(json.dumps(vercel_config, indent=2))
            generated.append(str(vercel_file))

        # === Fly.io (后端 API) ===
        if "fly" in deploy_type and project_config.backend:
            fly_content = self.FLY_TOML.format(
                app_name=project_config.name,
                port=project_config.backend.port,
                health=project_config.backend.health,
            )
            fly_file = project_path / "fly.toml"
            fly_file.write_text(fly_content)
            generated.append(str(fly_file))

            # Dockerfile
            be_path = project_path / project_config.backend.path
            dockerfile = be_path / "Dockerfile"
            if not dockerfile.exists():
                cmd_parts = project_config.backend.cmd.split()
                docker_content = self.DOCKERFILE_PYTHON.format(
                    port=project_config.backend.port,
                    cmd=project_config.backend.cmd,
                )
                dockerfile.write_text(docker_content)
                generated.append(str(dockerfile))

        # === Docker Compose ===
        if "docker" in deploy_type:
            compose_file = project_path / "docker-compose.prod.yml"
            if not compose_file.exists():
                compose = self._generate_compose(project_config)
                compose_file.write_text(compose)
                generated.append(str(compose_file))

        # === 上线检查清单 ===
        checklist = {
            "https": deploy_type in ("vercel", "fly", "vercel+fly"),
            "cors": project_config.backend is not None,
            "env_vars": len(project_config.env_required),
            "health_endpoint": project_config.backend.health if project_config.backend else None,
            "deploy_configs": generated,
        }

        report = {
            "deploy_type": deploy_type,
            "generated_files": generated,
            "checklist": checklist,
        }

        # 保存报告
        report_dir = Path(__file__).parent.parent / "reports" / project_config.name
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "L6-deploy-report.json").write_text(json.dumps(report, indent=2))

        result.finish("PASS", report=report)
        return result

    def _generate_compose(self, pc) -> str:
        services = {}
        if pc.backend:
            services["backend"] = {
                "build": {"context": f"./{pc.backend.path}", "dockerfile": "Dockerfile"},
                "ports": [f"{pc.backend.port}:{pc.backend.port}"],
                "env_file": [".env"],
                "restart": "unless-stopped",
            }
        if pc.frontend and pc.frontend.build:
            services["frontend"] = {
                "build": {"context": f"./{pc.frontend.path}", "dockerfile": "Dockerfile"},
                "ports": [f"{pc.frontend.port}:{pc.frontend.port}"],
                "restart": "unless-stopped",
            }

        import yaml
        return yaml.dump({"version": "3.8", "services": services}, default_flow_style=False)
```

## 验收标准
- [ ] L5 读取 L4 bug report 并生成修复 spec
- [ ] L5 调用 dispatch 执行修复
- [ ] L6 为 vercel 项目生成 vercel.json
- [ ] L6 为 fly 项目生成 fly.toml + Dockerfile
- [ ] L6 生成 .env.example
- [ ] L6 生成上线检查清单

## 不要做
- 不要实际执行部署（只生成配置）
- 不要修改已有的部署配置文件（只在不存在时创建）
- 不要修改其他层文件
