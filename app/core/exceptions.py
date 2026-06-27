from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": 0,
            "status_code": exc.status_code,
            "message": exc.detail,
            "result": None,
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": 0,
            "status_code": 422,
            "message": "Validation error",
            "result": exc.errors(),
        },
    )