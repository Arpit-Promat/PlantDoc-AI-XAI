"""Production WSGI entrypoint.

Use with Gunicorn:
    gunicorn -c gunicorn.conf.py wsgi:app
"""

from app import app

__all__ = ["app"]
