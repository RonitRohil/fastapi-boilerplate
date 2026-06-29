# FastAPI Boilerplate

A production-ready FastAPI boilerplate with JWT authentication, PostgreSQL, Alembic migrations, and a clean layered architecture. Built as a personal reference project — clone, configure, and extend.

## Features

- **Auth:** Signup, Login, Logout, Token Refresh, Forgot/Reset Password
- **JWT:** Access token + Refresh token + CSRF token (3-cookie pattern)
- **Session tracking:** `UserSession` and `UserToken` tables — real server-side revocation, not just JWT expiry
- **Password reset:** One-time-use tokens enforced server-side
- **Rate limiting:** `slowapi` on auth endpoints (`/login`, `/signup`, `/forgot/password`)
- **Password validation:** Minimum 8 chars, uppercase, digit required
- **User management:** CRUD endpoints with role-based access control (`user` / `admin`)
- **Architecture:** Router → Service → Repository → Model (strict layering, no business logic in routers)
- **Serialization:** Consistent `{ success, status_code, message, result }` response envelope on all routes
- **DB migrations:** Alembic with auto-generate support
- **Pydantic v2 + SQLAlchemy 2.x**
- **Tests:** pytest suite with SQLite in-memory test DB

## Stack

| Layer         | Technology                      |
| ------------- | ------------------------------- |
| Framework     | FastAPI 0.111                   |
| Database      | PostgreSQL (via psycopg2)       |
| ORM           | SQLAlchemy 2.0                  |
| Migrations    | Alembic 1.13                    |
| Validation    | Pydantic v2                     |
| Auth          | PyJWT + bcrypt                  |
| Rate limiting | slowapi                         |
| Dev tooling   | ruff, black, pre-commit, pytest |

## Project Structure

```
app/
├── core/
│   ├── config.py          # Settings (pydantic-settings, .env)
│   ├── database.py        # SQLAlchemy engine + session
│   ├── dependencies.py    # FastAPI dependencies (get_db, get_current_user, require_admin, verify_csrf_token)
│   ├── exceptions.py      # Global HTTP + validation exception handlers
│   ├── rate_limit.py      # slowapi limiter instance
│   ├── response.py        # api_response() — consistent JSON envelope
│   └── security.py        # JWT creation/decode, bcrypt, CSRF
├── middleware/
│   └── logging_middleware.py  # Request/response timing logger
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
│   ├── auth.py            # LoginRequest, SignupRequest, etc.
│   ├── user.py            # UserCreate, UserUpdate, UserResponse, etc.
│   └── response.py        # APIResponse generic envelope
├── services/
│   ├── auth_service.py    # Signup, login, refresh, logout, forgot/reset password
│   └── user_service.py    # User CRUD business logic
└── main.py                # FastAPI app + router registration + middleware
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
FIRST_ADMIN_PASSWORD=YourStrongPassword1
COOKIE_SECURE=false
```

> **Important:** `SECRET_KEY` and `FIRST_ADMIN_PASSWORD` are required — the app will refuse to start without them.

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
POST /api/v1/auth/signup   → 201, sets 3 cookies, returns { user }
POST /api/v1/auth/login    → 200, sets 3 cookies, returns { user }
POST /api/v1/auth/refresh  → reads refresh_token cookie, rotates access_token cookie
POST /api/v1/auth/logout   → reads refresh_token cookie, deletes all 3 cookies
```

Three cookies are set on login/signup:

| Cookie          | httpOnly | Purpose                                                                     |
| --------------- | -------- | --------------------------------------------------------------------------- |
| `access_token`  | Yes      | JWT access token — JS cannot read                                           |
| `refresh_token` | Yes      | JWT refresh token — path-restricted to `/api/v1/auth`                       |
| `csrf_token`    | No       | JS-readable CSRF token — send as `X-CSRF-Token` header on mutating requests |

### Bearer token (API clients / Swagger UI)

```bash
# Login — get access_token from Set-Cookie response header (or body is stripped by design)
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "YourPassword1"}'

# Subsequent requests — send cookie jar
curl -b cookies.txt http://localhost:8000/api/v1/users/me
```

In Swagger UI: call `/login` → open browser DevTools → copy `access_token` cookie value → click **Authorize** → paste as Bearer token.

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path               | Auth          | Description                     |
| ------ | ------------------ | ------------- | ------------------------------- |
| POST   | `/signup`          | Public        | Register new user (201)         |
| POST   | `/login`           | Public        | Login, set auth cookies         |
| POST   | `/refresh`         | Cookie        | Rotate access token             |
| POST   | `/logout`          | Cookie + CSRF | Revoke session, clear cookies   |
| POST   | `/forgot/password` | Public        | Initiate password reset         |
| POST   | `/reset/password`  | Public        | Reset password (one-time token) |

### Users (`/api/v1/users`)

| Method | Path                       | Auth         | Description                        |
| ------ | -------------------------- | ------------ | ---------------------------------- |
| GET    | `/me`                      | Any user     | Get own profile                    |
| PUT    | `/update/me`               | Self + CSRF  | Update own name                    |
| POST   | `/create`                  | Admin        | Create a user                      |
| GET    | `/get/list`                | Any user     | List users (paginated, filterable) |
| GET    | `/get/{user_id}`           | Any user     | Get user by ID                     |
| PUT    | `/update/{user_id}`        | Admin + CSRF | Update any user                    |
| PUT    | `/{user_id}/update/status` | Admin + CSRF | Toggle active/inactive             |
| DELETE | `/delete/{user_id}`        | Admin        | Delete user                        |

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
  .split("; ")
  .find((row) => row.startsWith("csrf_token="))
  ?.split("=")[1];

fetch("/api/v1/users/update/me", {
  method: "PUT",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": csrfToken,
  },
  body: JSON.stringify({ first_name: "New Name" }),
});
```

API clients using Bearer tokens (no cookies) bypass CSRF — this is intentional.

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Tests use an in-memory SQLite database and cover:

- Signup/login success and failure cases
- Password complexity validation
- Refresh and logout flows
- One-time-use password reset token enforcement
- CSRF protection
- Role-based access control

## Dev Tools

```bash
black app/          # format
ruff check app/     # lint
pre-commit install  # install git hooks
```

## Password Requirements

All passwords (signup, admin create, reset) must be:

- At least 8 characters
- At least one uppercase letter
- At least one digit

## Notes for Existing Deployments

If you are upgrading an existing database, run a migration to make `user_tokens.session_id` nullable and remove its FK constraint (required for password reset token storage):

```sql
ALTER TABLE user_tokens DROP CONSTRAINT user_tokens_session_id_fkey;
ALTER TABLE user_tokens ALTER COLUMN session_id DROP NOT NULL;
```

Or generate it via Alembic:

```bash
alembic revision --autogenerate -m "make_user_token_session_id_nullable"
alembic upgrade head
```

## License

MIT
