"""Production Gunicorn configuration for ATHARVADRISHTI.

The Flask application remains unchanged at the UI level. Gunicorn can run
multiple worker processes so requests can be distributed across workers.
Tune WEB_CONCURRENCY at deployment time based on available CPU and RAM,
because each worker loads the TensorFlow models into its own process.
"""

import multiprocessing
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = int(os.getenv("WEB_CONCURRENCY", max(1, multiprocessing.cpu_count())))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")
timeout = int(os.getenv("GUNICORN_TIMEOUT", "180"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "500"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "50"))
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "0") == "1"
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
