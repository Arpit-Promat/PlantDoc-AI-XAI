# ATHARVADRISHTI Security

Phase 2 hardens the existing Flask backend without changing the current frontend/UI.

## Implemented

- Strong production `SECRET_KEY` requirement (minimum 32 characters).
- Secure Flask session-cookie defaults: HttpOnly and SameSite=Lax; Secure can be enabled with `COOKIE_SECURE=1`.
- Request body limits through `MAX_CONTENT_LENGTH` and `MAX_FORM_MEMORY_SIZE`.
- Image upload validation using extension, MIME type, size and Pillow image verification.
- Random UUID filenames instead of a predictable fixed upload filename.
- Generic user-facing errors so internal model/path/database details are not exposed.
- Security response headers including `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and a CSP report-only policy.
- Optional HSTS with `FORCE_HTTPS=1`.
- Optional host allowlist with `TRUSTED_HOSTS`.
- Password hashing with Werkzeug's password hashing helpers.
- JWT authentication using HS256 with required `sub`, `iat`, `exp`, and `iss` claims.
- `/api/auth/register`, `/api/auth/login`, and `/api/auth/me` endpoints.
- Scan history/detail endpoints require authentication and are restricted to the authenticated user's records.
- Rate limiting: 5 requests/minute for registration/login and 20 POST prediction requests/minute.

## Production configuration

Set at least:

```text
FLASK_DEBUG=0
SECRET_KEY=<random secret of at least 32 characters>
COOKIE_SECURE=1
FORCE_HTTPS=1
RATELIMIT_STORAGE_URI=redis://<host>:<port>/<db>
```

For deployed environments, use PostgreSQL through `DATABASE_URL` and Redis as the rate-limit store. The local `memory://` rate-limit backend is intended only for development and does not coordinate limits across multiple application instances.

## Authentication API

Register:

```http
POST /api/auth/register
Content-Type: application/json

{"name":"Farmer","email":"farmer@example.com","password":"strong-password"}
```

Login:

```http
POST /api/auth/login
Content-Type: application/json

{"email":"farmer@example.com","password":"strong-password"}
```

Use the returned access token for protected endpoints:

```http
Authorization: Bearer <access_token>
```

The existing prediction page remains available without requiring a new login screen, preserving the existing UI.
