from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ...utils.api_response import ApiResponse, ApiResponseError
from .api_schema import DEFAULT_STATUS_CODE, DESCRIPTION, ResponseClass, RESPONSES
import logging

router = APIRouter()


@router.get(
    "/",
    status_code=DEFAULT_STATUS_CODE,
    description=DESCRIPTION,
    responses=RESPONSES,
    response_model=ResponseClass,
)
async def health_status() -> JSONResponse:
    try:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                ResponseClass(
                    message="Health status OK",
                )
            ),
        )
    except Exception as e:
        logging.exception(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ResponseClass(
                    message="Internal server error",
                    error=ApiResponseError(
                        message=str(e),
                        code="UNK",
                    ),
                )
            ),
        )
