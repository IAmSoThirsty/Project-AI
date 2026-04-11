=== PORT CONFIGURATION AUDIT ===

DEVELOPMENT PORTS (.env):

- API_PORT: 8001 (FastAPI main application)
- METRICS_PORT: 8000 (Prometheus metrics)
- CORS_ORIGINS: 8000, 3000, 5000

DOCKER COMPOSE PORTS:

- App (Flask/API): 5000:5000, 8000:8000
- Prometheus: 9090:9090
- Alertmanager: 9093:9093
- Grafana: 3000:3000
- Temporal: 7233:7233 (gRPC), 8233:8233 (UI)
- Agent Workers: 8011-8018 (8 workers mapping internal 8000)

TEMPORAL WORKFLOW:

- Host: temporal:7233
- UI: localhost:8233

DATABASE:

- PostgreSQL: 5432 (internal to docker network)
- Database URL: postgresql://temporal:temporal@temporal-postgresql:5432/temporal

ALL PORTS PROPERLY CONFIGURED ✅
No port conflicts detected ✅
