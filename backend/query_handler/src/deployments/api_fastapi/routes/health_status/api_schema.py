from fastapi import status
from ...utils.api_response import ApiResponse, ApiResponseError

DEFAULT_STATUS_CODE = status.HTTP_200_OK

ResponseClass = ApiResponse[None]

DESCRIPTION = "Check the health status of the API"

RESPONSES = {
    status.HTTP_200_OK: {
        "description": "Health status OK",
        "model": ResponseClass,
        "content": {
            "application/json": {
                "example": {
                    "message": "Health status OK",
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "model": ResponseClass,
        "content": {
            "application/json": {
                "example": {
                    "message": "Internal server error",
                    "error": {
                        "message": "Error message",
                        "code": "UNK",
                    },
                }
            }
        },
    },
}
