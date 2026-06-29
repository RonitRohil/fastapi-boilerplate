from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.core.rate_limit import limiter
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import users_router, auth_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(LoggingMiddleware)

app.include_router(users_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
