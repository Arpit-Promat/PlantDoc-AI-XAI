# Phase 3 — Scalability

## Architecture

```text
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │                     │
          Flask/Gunicorn         Flask/Gunicorn
           Web Instance           Web Instance
                │                     │
                └──────────┬──────────┘
                           │
                    PostgreSQL DB
                           │
                ┌──────────┴──────────┐
                │                     │
             Redis              Celery Workers
                                      │
                                TensorFlow Models
```

## What Phase 3 adds

- Production WSGI entrypoint: `wsgi.py`.
- Gunicorn configuration with tunable worker count and worker recycling.
- PostgreSQL connection pooling and health/readiness endpoints.
- Redis-ready distributed rate-limit storage.
- Optional Celery + Redis background inference.
- `/api/scans/async` creates a queued scan and returns HTTP 202.
- `/api/scans/<id>/status` lets clients poll the job state.
- Docker image for repeatable deployment.
- Docker Compose stack containing web, worker, Redis and PostgreSQL.
- Shared upload volume between web and worker containers.

## Existing UI remains unchanged

The current synchronous `/` route continues to work as before. The asynchronous
scan API is an additive backend capability and does not require any modification
to the existing HTML/CSS/Streamlit interface.

## Running locally

### Existing UI

```bash
python app.py
```

### Production web server

```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

### Background worker

Start Redis first, then:

```bash
celery -A tasks.celery worker --loglevel=INFO --concurrency=1
```

### Full local stack

```bash
docker compose up --build
```

## Production recommendations

Use PostgreSQL rather than SQLite when running multiple web instances. Configure
`DATABASE_URL`, `SECRET_KEY`, and `RATELIMIT_STORAGE_URI` through deployment
secrets/environment variables.

For multiple hosts, replace the shared local upload volume with object storage
such as S3-compatible storage. The current local filesystem implementation is
suitable for one host or a shared filesystem, but object storage is the intended
next step for truly stateless horizontal scaling.

TensorFlow models are loaded per Gunicorn/Celery process. Increase worker counts
only after measuring available RAM/CPU; more workers are not automatically better.

SHAP remains an expensive explanation step. Keep it outside the main web worker
pool for high-volume deployments or move explanation generation to a separate
background queue.
