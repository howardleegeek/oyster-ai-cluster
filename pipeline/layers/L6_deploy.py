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
