from fastapi import status
from ...utils.api_response import ApiResponse, ApiResponseError
from .api_models import SimilarProductsResponseModel

DEFAULT_STATUS_CODE = status.HTTP_201_CREATED

ResponseClass = ApiResponse[SimilarProductsResponseModel]

DESCRIPTION = "Search for similar products based on the query"

RESPONSES = {
    status.HTTP_201_CREATED: {
        "description": "Query Similar Products successful",
        "model": ResponseClass,
        "content": {
            "application/json": {
                "example": {
                    "message": "Query Similar Products successful",
                    "data": {
                        "similar_products": [
                            {
                                "product_id": "string",
                                "name": "string",
                                "main_category": "string",
                                "sub_category": "string",
                                "image_url": "string",
                                "ratings": 0,
                                "discount_price": 0,
                                "actual_price": 0,
                                "modified_date": "2023-11-01T12:31:52.000Z",
                                "created_date": "2023-11-01T12:31:52.000Z",
                                "score": 0,
                            }
                        ],
                        "query": "string",
                        "created_date": "2023-11-01T12:31:52.000Z",
                        "modified_date": "2023-11-01T12:31:52.000Z",
                    },
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
