<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

<h1 align="center">🔐 Sovereign Data Vault Layer</h1>

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-MASTER--TIER-gold?style=for-the-badge" alt="Status: Master Tier" />
  <img src="https://img.shields.io/badge/SECURITY-SOVEREIGN-red?style=for-the-badge" alt="Security: Sovereign" />
  <img src="https://img.shields.io/badge/COMPLIANCE-ToG--LEVEL-blue?style=for-the-badge" alt="Compliance: ToG Level" />
</p>

Zero-knowledge encryption layer with capability-based access control. Ensures data is provably inaccessible without explicit cryptographic user consent.

## 🚀 Features

- ✅ **Production-Ready**: Full observability, security, and reliability features
- ✅ **Authentication**: both authentication
- ✅ **Rate Limiting**: 500 requests/minute
- ✅ **Metrics**: Prometheus metrics at `/metrics`
- ✅ **Health Checks**: Liveness, readiness, and startup probes
- ✅ **Auto-Scaling**: Horizontal Pod Autoscaler (2-10 replicas)
- ✅ **CI/CD**: Automated pipelines with security scanning
- ✅ **Database**: in_memory with migrations
- ✅ **Structured Logging**: JSON logs with request tracing
- ✅ **API Documentation**: OpenAPI/Swagger at `/api/v1/docs`

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized development)
- Kubernetes cluster (for production deployment)

## 🛠️ Quick Start

### Local Development

1. **Clone the repository**

```bash
git clone <repository-url>
cd Sovereign Data Vault Layer
```

1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

1. **Run database** (if not using in-memory)

```bash
```

1. **Start the service**

```bash
python -m app.main
```

The service will be available at `http://localhost:8000`

### Docker

```bash
# Build image
docker build -t Sovereign Data Vault Layer:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  Sovereign Data Vault Layer:latest
```

### Docker Compose

```bash
docker-compose up
```

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: <http://localhost:8000/api/v1/docs>
- **ReDoc**: <http://localhost:8000/api/v1/redoc>
- **OpenAPI JSON**: <http://localhost:8000/api/v1/openapi.json>

## 🔒 Authentication

This service uses **both** authentication.

### API Key Authentication

Include your API key in the request header:

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/items
```

### JWT Authentication

Include your JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer your-jwt-token" \
  http://localhost:8000/api/v1/items
```

## 🏗️ Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### Key Components

- **API Layer**: FastAPI with async support
- **Business Logic**: Service layer with domain logic
- **Data Access**: Repository pattern with database abstraction
- **Middleware**: Request ID, metrics, rate limiting, authentication
- **Observability**: Structured logging, Prometheus metrics, health checks

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run integration tests
pytest tests/integration/
```

## 🚢 Deployment

### Kubernetes

1. **Apply manifests**

```bash
kubectl apply -f kubernetes/
```

1. **Check deployment status**

```bash
kubectl rollout status deployment/Sovereign Data Vault Layer
```

1. **View logs**

```bash
kubectl logs -f deployment/Sovereign Data Vault Layer
```

### CI/CD Pipeline

This project includes automated CI/CD pipelines:

- **Continuous Integration**: `.github/workflows/ci.yml`
  - Linting, type checking, security scanning
  - Unit tests with 100% coverage requirement
  - Integration tests
  - Vulnerability scanning
  - SBOM generation

- **Continuous Deployment**: `.github/workflows/cd.yml`
  - Automated deployment to dev/staging/production
  - Database migrations
  - Smoke tests
  - Automatic rollback on failure

## 📊 Monitoring

### Metrics

Prometheus metrics are exposed at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Key metrics:

- `service_sovereign_data_vault_layer_requests_total` - Total requests
- `service_sovereign_data_vault_layer_request_duration_seconds` - Request latency
- `service_sovereign_data_vault_layer_requests_inflight` - In-flight requests
- `service_sovereign_data_vault_layer_db_query_duration_seconds` - Database query latency

### Health Checks

- **Health**: `/health` - Basic health check
- **Readiness**: `/health/ready` - Ready to accept traffic
- **Liveness**: `/health/live` - Service is alive
- **Startup**: `/health/startup` - Service has started

## 🐛 Troubleshooting

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for operational procedures and troubleshooting.

Common issues:

1. **Service won't start**: Check database connection in `.env`
2. **Authentication errors**: Verify API keys/JWT secret in `.env`
3. **Performance issues**: Check Prometheus metrics and logs

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Failure Modes](docs/FAILURE_MODES.md)
- [Performance](docs/PERFORMANCE.md)
- [Runbook](docs/RUNBOOK.md)
- [Security](docs/SECURITY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

© 2026 Jeremy Karrick (IAmSoThirsty). All Rights Reserved. Licensed under the Project-AI Sovereign Framework (MIT Open Source for core, Proprietary for Governance).

## 📞 Support

For support, email <support@example.com> or open an issue in the repository.
