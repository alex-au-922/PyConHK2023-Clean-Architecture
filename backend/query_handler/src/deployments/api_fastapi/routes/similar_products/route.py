from datetime import datetime
from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ...utils.api_response import ApiResponseError
from .api_schema import DEFAULT_STATUS_CODE, DESCRIPTION, ResponseClass, RESPONSES
from .api_models import SimilarProductsRequestModel
from usecases import (
    EmbedRawQueryDetailsUseCase,
    QuerySimilarProductDetailsUseCase,
    FetchRawProductDetailsUseCase,
)
from entities import RawQueryDetails
import logging
from typing import cast

router = APIRouter()


@router.post(
    "/similar_products",
    status_code=DEFAULT_STATUS_CODE,
    description=DESCRIPTION,
    responses=RESPONSES,
    response_model=ResponseClass,
)
def similar_products(
    request: Request,
    request_model: SimilarProductsRequestModel,
) -> JSONResponse:
    try:
        raw_query_details = RawQueryDetails(
            query=request_model.query, created_date=datetime.now()
        )

        embedded_query_details = cast(
            EmbedRawQueryDetailsUseCase,
            request.app.state.embed_raw_query_details_client,
        ).embed(raw_query_details)

        if embedded_query_details is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(
                    ResponseClass(
                        message="Query Embedding failed",
                        error=ApiResponseError(
                            message=str(e),
                            code="QUERY_EMBEDDING_FAILED",
                        ),
                    )
                ),
            )

        similar_products_tuples = cast(
            QuerySimilarProductDetailsUseCase,
            request.app.state.query_similar_product_details_client,
        ).query(
            embedded_query_details,
            request_model.threshold,
            request_model.limit,
        )

        logging.info(f"{similar_products_tuples = }")

        if similar_products_tuples is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(
                    ResponseClass(
                        message="Query Similar Products failed",
                        error=ApiResponseError(
                            message=str(e),
                            code="QUERY_SIMILAR_PRODUCTS_FAILED",
                        ),
                    )
                ),
            )

        similar_product_ids = [product_id for product_id, _ in similar_products_tuples]
        similar_product_scores = [score for _, score in similar_products_tuples]

        similar_product_details = cast(
            FetchRawProductDetailsUseCase,
            request.app.state.fetch_raw_product_details_client,
        ).fetch(similar_product_ids)

        logging.info(f"{similar_product_details = }")

        if similar_product_details is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(
                    ResponseClass(
                        message="Fetch Similar Products failed",
                        error=ApiResponseError(
                            message=str(e),
                            code="FETCH_SIMILAR_PRODUCTS_FAILED",
                        ),
                    )
                ),
            )

        valid_similar_product_details = [
            product for product in similar_product_details if product is not None
        ]

        valid_similar_product_scores = [
            score
            for score, product in zip(similar_product_scores, similar_product_details)
            if product is not None
        ]

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(
                ResponseClass(
                    message="Query Similar Products successful",
                    data={
                        "similar_products": [
                            {
                                "product_id": product.product_id,
                                "name": product.name,
                                "main_category": product.main_category,
                                "sub_category": product.sub_category,
                                "image_url": product.image_url,
                                "ratings": product.ratings,
                                "discount_price": product.discount_price,
                                "actual_price": product.actual_price,
                                "modified_date": product.modified_date,
                                "created_date": product.created_date,
                                "score": min(1, max(-1, score)),
                            }
                            for product, score in zip(
                                valid_similar_product_details,
                                valid_similar_product_scores,
                            )
                        ],
                        "query": request_model.query,
                        "created_date": datetime.now(),
                        "modified_date": datetime.now(),
                    },
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
