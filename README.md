# FastAPI Boilerplate

A production-ready FastAPI boilerplate with JWT authentication, PostgreSQL, Alembic migrations, and a clean layered architecture. Built as a personal reference project — clone, configure, and extend.

## Features

- **Auth:** Signup, Login, Logout, Token Refresh, Forgot/Reset Password
- **JWT:** Access token + Refresh token + CSRF token (3-cookie pattern)
- **Session tracking:** `UserSession` and `UserToken` tables — real server-side revocation, not just JWT expiry
- **User management:** CRUD endpoints with role-based access control (`user` / `admin`)
- **Architecture:** Router → Service → Repository → Model (strict layering, no business logic in routers)
- **Serialization:** Consistent `{ success, status_code, message, result }` response envelope on all routes
- **DB migrations:** Alembic with auto-generate support
- **Pydantic v2 + SQLAlchemy 2.x**

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL (via psycopg2) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic 1.13 |
| Validation | Pydantic v2 |
| Auth | PyJWT + bcrypt |
| Dev tooling | ruff, black, pre-commit, pytest |

## Project Structure

```
app/
├── core/
│   ├── config.py          # Settings (pydantic-settings, .env)
│   ├── database.py        # SQLAlchemy engine + session
│   ├── dependencies.py    # FastAPI dependencies (get_db, get_current_user, require_admin, verify_csrf_token)
│   ├── exceptions.py      # Global HTTP + validation exception handlers
│   ├── response.py        # api_response() — consistent JSON envelope
│   └── security.py        # JWT creation/decode, bcrypt, CSRF
├── middleware/
│   └── logging_middleware.py
├── models/
│   ├── user.py            # User ORM model
│   └── auth.py            # UserSession, UserToken ORM models
├── repositories/
│   ├── user_repository.py # DB queries for users
│   └── auth_repository.py # DB queries for sessions + tokens
├── routers/
│   ├── auth_router.py     # /api/v1/auth/* endpoints
│   └── users_router.py    # /api/v1/users/* endpoints
├── schemas/
│   ├── auth.py            # LoginRequest, SignupRequest, TokenResponse, etc.
│   ├── user.py            # UserCreate, UserUpdate, UserResponse, etc.
│   └── response.py        # APIResponse generic envelope
├── services/
│   ├── auth_service.py    # Signup, login, refresh, logout, forgot/reset password
│   └── user_service.py    # User CRUD business logic
└── main.py                # FastAPI app + router registration
alembic/                   # DB migration scripts
tests/                     # pytest suite (conftest, test_auth, test_users)
```

## Quick Start

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd fastapi-boilerplate
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements-dev.txt
```

### 2. Configure `.env`

Copy `.env.example` to `.env` and fill in your values:

```env
APP_NAME="FastAPI Boilerplate"
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql://fastapi_user:yourpassword@localhost:5432/fastapi_boilerplate
SECRET_KEY=your-super-secret-key-minimum-32-chars-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=Admin@1234
COOKIE_SECURE=false
```

> **Important:** Never commit `.env`. Add it to `.gitignore`.

### 3. Set up PostgreSQL

```sql
CREATE DATABASE fastapi_boilerplate;
CREATE USER fastapi_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE fastapi_boilerplate TO fastapi_user;
```

### 4. Run migrations

```bash
alembic upgrade head
```

If starting fresh with no migration files:

```bash
alembic revision --autogenerate -m "create_tables"
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

API: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

## Auth Flow

### Cookie-based (browser clients)

```
POST /api/v1/auth/signup   → sets 3 cookies
POST /api/v1/auth/login    → sets 3 cookies
POST /api/v1/auth/refresh  → rotates access_token cookie
POST /api/v1/auth/logout   → deletes all 3 cookies
```

Three cookies are set on login/signup:

| Cookie | httpOnly | Purpose |
|--------|----------|---------|
| `access_token` | Yes | JWT access token — JS cannot read |
| `refresh_token` | Yes | JWT refresh token — path-restricted to `/api/v1/auth/refresh` |
| `csrf_token` | No | JS-readable CSRF token — send as `X-CSRF-Token` header on mutating requests |

### Bearer token (API clients / Swagger UI)

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# Use the access_token from the response
curl http://localhost:8000/api/v1/users/get/list \
  -H "Authorization: Bearer <access_token>"
```

In Swagger UI: call `/login` → copy `access_token` → click **Authorize** (top right) → paste token → all protected routes auto-inject it.

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/signup` | Public | Register new user |
| POST | `/login` | Public | Login, get tokens |
| POST | `/refresh` | Public | Refresh access token |
| POST | `/logout` | Public | Revoke session + clear cookies |
| POST | `/forgot/password` | Public | Send password reset link |
| POST | `/reset/password` | Public | Reset password with token |

### Users (`/api/v1/users`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/create` | Admin | Create a user |
| GET | `/get/list` | Any user | List users (paginated, filterable) |
| GET | `/get/{user_id}` | Any user | Get user by ID |
| PUT | `/update/me` | Self | Update own profile (name only) |
| PUT | `/update/{user_id}` | Admin | Update any user |
| PUT | `/{user_id}/update/status` | Admin | Toggle user active/inactive |
| DELETE | `/delete/{user_id}` | Admin | Delete user |

## Response Format

All responses follow a consistent envelope:

```json
{
  "success": 1,
  "status_code": 200,
  "message": "User logged in successfully",
  "result": { ... }
}
```

Errors:

```json
{
  "success": 0,
  "status_code": 400,
  "message": "Invalid email or password",
  "result": null
}
```

## CSRF Protection

State-changing requests from a browser require the `X-CSRF-Token` header:

```javascript
// Read the csrf_token cookie (it's not httpOnly)
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrf_token='))
  ?.split('=')[1];

fetch('/api/v1/users/update/me', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken,
  },
  body: JSON.stringify({ first_name: 'Ronit' }),
});
```

API clients using Bearer tokens (no cookies) bypass CSRF — this is intentional.

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Dev Tools

```bash
black app/          # format
ruff check app/     # lint
pre-commit install  # install hooks
```

## Known Limitations

- Password reset token is not one-time-use (reusable within 15-minute window)
- No rate limiting on auth endpoints (slowapi installed, not yet wired)
- No email delivery for password reset (token returned in response when `DEBUG=true`)
- No password complexity validation
- Test suite scaffolded but not yet implemented

See `CODE_REVIEW.md` for the full issue tracker with fix details.

## License

MIT
