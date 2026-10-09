# devops-todo-api (TaskBoard)

A small 3-tier web application (web page + REST API + database) built as a **DevOps learning project**. The application is
simple on purpose; the point is the delivery pipeline around it.

```
 git push ──► GitHub Actions ──► 1. unit tests (Python 3.12 + 3.13)
                                 2. start the real stack with Docker Compose
                                    (Nginx + API + PostgreSQL) and smoke-test it
                                 3. build both images and publish them to GHCR
                                         │
                                         ▼
                              ghcr.io/<user>/devops-todo-api:<run-number>  (API)
                              ghcr.io/<user>/devops-todo-api-frontend:<run-number>  (Nginx)

 Browser ──► Nginx :80 ──┬─► /      static web page
                         └─► /api/  ──► Flask/Gunicorn :8000 ──► PostgreSQL
```

## Stack

| Piece | Tool |
|---|---|
| Web page + reverse proxy | HTML/JavaScript served by Nginx |
| API | Python, Flask, Flask-SQLAlchemy, Gunicorn |
| Database | PostgreSQL 16 (SQLite in unit tests) |
| Packaging | Docker (slim base image, non-root user, health check) |
| Local / server run | Docker Compose (three containers, DB health-gated start-up, only Nginx is public) |
| CI/CD | GitHub Actions (test, integration test, publish to GHCR) |

## Run it on any machine with Docker

```bash
git clone https://github.com/<your-user>/devops-todo-api.git
cd devops-todo-api
cp .env.example .env          # then edit .env and choose a password
docker compose up -d --build
bash scripts/smoke_test.sh
```

Open `http://localhost/` (or `http://<server-ip>/`) for the web page. Try the API through Nginx:

```bash
curl http://localhost/api/health
curl -X POST http://localhost/api/todos -H 'Content-Type: application/json' -d '{"title":"learn docker"}'
curl http://localhost/api/todos
curl -X PUT  http://localhost/api/todos/1 -H 'Content-Type: application/json' -d '{"done":true}'
curl -X DELETE http://localhost/api/todos/1
```

Stop it: `docker compose down` (keep data) or `docker compose down -v` (delete data).

## Run the unit tests without Docker

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
```

## Design decisions

- **Dependencies are copied and installed before the code** in the Dockerfile, so
  rebuilds after a code-only change are fast (layer cache).
- **The container runs as a non-root user** and has a `HEALTHCHECK`.
- **Compose waits for Postgres to be healthy** before starting the API.
- **Secrets are not in Git.** The database password lives in `.env` (ignored by
  Git); CI generates a throw-away one for each run.
- **Unit tests use SQLite**, so they are fast and need no services; the
  integration job tests against real PostgreSQL.
- **Images are tagged with the run number** (and `latest`), so every build is traceable.

## Roadmap

- [ ] Terraform: create the EC2 server and security group
- [ ] Deploy job: pull the new image on the server over SSH
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Move to Kubernetes (k3s) with Argo CD
