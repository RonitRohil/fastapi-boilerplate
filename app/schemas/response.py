# app/schemas/response.py
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: int = 1
    status_code: int = 200
    message: str = "Success"
    result: Optional[T] = None
