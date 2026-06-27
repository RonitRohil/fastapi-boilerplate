from typing import Any, Optional
from fastapi.responses import JSONResponse
from app.schemas.response import APIResponse


def api_response(
    success: int = 1,
    status_code: int = 200,
    message: str = "Success",
    result: Any = None,
) -> JSONResponse:
    body = APIResponse(
        success=success,
        status_code=status_code,
        message=message,
        result=result,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
    )
