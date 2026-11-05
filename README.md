# URL Shortener — Cloud-Native DevSecOps Project

A containerised URL Shortener API built with Python Flask, PostgreSQL and Redis, deployed on Kubernetes and integrated with an automated DevSecOps pipeline using GitHub Actions, Trivy and GitHub Container Registry (GHCR).

## Architecture

```mermaid
flowchart TB
    U[User] --> N[Nginx Reverse Proxy]
    N --> A[Flask REST API]

    A --> P[(PostgreSQL)]
    A --> R[(Redis Cache)]

    G[GitHub Repository] --> C[GitHub Actions CI/CD]
    C --> T[Trivy Security Scanning]
    T --> H[GitHub Container Registry]
    H --> K[Kubernetes - Minikube]
    K --> A

The application uses a modular architecture:

- **Flask:** REST API and URL redirection.
- **PostgreSQL:** Persistent storage for shortened URLs.
- **Redis:** Caching layer for faster URL lookups.
- **Docker:** Application containerisation.
- **Nginx:** Reverse proxy.
- **Kubernetes (Minikube):** Container orchestration.
- **GitHub Actions:** CI/CD automation.
- **Trivy:** Vulnerability and secret scanning.
- **GHCR:** Docker image registry.

## Features

- Generate unique short URLs.
- Redirect users to original URLs.
- Validate submitted URLs.
- Store URL records in PostgreSQL.
- Cache frequently accessed URLs in Redis.
- Health endpoint for application and dependency checks.
- Automated application tests.
- Docker image build and security scanning.
- Automated publishing to GitHub Container Registry.
- Kubernetes deployment using the published container image.

## Technology Stack

| Category | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Cache | Redis |
| Reverse Proxy | Nginx |
| Containers | Docker |
| Orchestration | Kubernetes, Minikube |
| CI/CD | GitHub Actions |
| Security | Trivy |
| Registry | GitHub Container Registry |
| Testing | Pytest |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/shorten` | Generate a short URL |
| GET | `/<code>` | Redirect to original URL |
| GET | `/health` | Check application and dependency health |

### Create a short URL

```bash
curl -X POST http://localhost:8081/shorten \
-H "Content-Type: application/json" \
-d '{"url":"https://github.com"}'
```

Example response:

```json
{
  "original_url": "https://github.com",
  "short_code": "abc123",
  "short_url": "http://localhost:8081/abc123"
}
```

### Health check

```bash
curl http://localhost:8081/health
```

## DevSecOps Pipeline

Every push to the main branch triggers the GitHub Actions workflow.

1. Checkout application source.
2. Set up Python.
3. Install dependencies.
4. Validate Python syntax.
5. Execute automated tests.
6. Check dependencies.
7. Build Docker image.
8. Scan source code for vulnerabilities and secrets using Trivy.
9. Scan the Docker image using Trivy.
10. Authenticate to GitHub Container Registry.
11. Build and publish the Docker image.

Published image:

```bash
docker pull ghcr.io/kelvinarigbe/url-shortener:latest
```

## Kubernetes Deployment

The application was deployed locally using Minikube.

The deployment uses the published GHCR image:

```text
ghcr.io/kelvinarigbe/url-shortener:latest
```

Check deployment status:

```bash
kubectl get deployments
kubectl get pods
```

Inspect the deployed image:

```bash
kubectl get deployment urlshortener-app \
-o jsonpath='{.spec.template.spec.containers[*].image}'
```

Forward the application service:

```bash
kubectl port-forward svc/urlshortener-service 8081:5000
```

The API is then accessible at:

```text
http://127.0.0.1:8081
```

## Testing

Run automated tests:

```bash
python -m pytest -v
```

The test suite covers URL creation, input validation, cache-based redirects and database fallback.

## Repository Structure

```text
url-shortener/
├── .github/
│   └── workflows/
│       └── ci.yml
├── k8s/
├── nginx/
├── tests/
│   └── test_app.py
├── app.py
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Engineering Outcomes

This project demonstrates practical experience with:

- Building and containerising a REST API.
- Integrating relational databases and caching.
- Deploying workloads on Kubernetes.
- Implementing automated CI/CD workflows.
- Integrating container and source security scanning.
- Publishing versioned container images.
- Troubleshooting Kubernetes image pulls, deployments and application connectivity.

## Author

**Kelvin Arigbe**

Cloud Security | DevOps | DevSecOps | Azure

GitHub: https://github.com/KelvinArigbe
