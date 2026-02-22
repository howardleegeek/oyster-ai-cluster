## 目标
Deploy PostHog analytics platform via Docker on GCP glm-node-2 with all required services

## 约束
- Use official PostHog docker-compose from https://posthog.com/docs/self-host/deploy/docker
- Services: posthog, postgres, redis, clickhouse, zookeeper, kafka
- Data volumes: /opt/posthog/postgres, /opt/posthog/clickhouse
- Port 8000 exposed
- Min resources: 4GB RAM, 2 CPU (verify GCP node)
- GCP node: glm-node-2
- Run as systemd service

## 验收标准
- [ ] docker-compose.yml created in /opt/posthog/
- [ ] All 6+ containers running healthy
- [ ] PostHog web UI accessible on http://glm-node-2:8000
- [ ] Database migrations completed successfully
- [ ] docker-compose ps shows all services healthy
- [ ] Service survives reboot (systemd enabled)
- [ ] curl http://localhost:8000/_health returns 200

## 不要做
- 不要创建 projects (B04 handles)
- 不要配置 SMTP
- 不要开放公网访问
- 不要修改 ClickHouse schema