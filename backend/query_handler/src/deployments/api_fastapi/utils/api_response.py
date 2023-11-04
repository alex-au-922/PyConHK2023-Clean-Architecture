from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponseError(BaseModel):
    message: str
    code: str


class ApiResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    error: Optional[ApiResponseError] = None
