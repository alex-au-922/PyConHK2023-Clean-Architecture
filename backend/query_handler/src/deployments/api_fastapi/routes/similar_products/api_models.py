from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class SimilarProductsRequestModel(BaseModel):
    query: str
    limit: Optional[int] = None
    threshold: Optional[float] = None

    @field_validator("limit")
    def limit_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("limit must be non-negative!")
        return v

    @field_validator("threshold")
    def threshold_must_within_range(cls, v):
        if v < -1 or v > 1:
            raise ValueError("threshold must be between -1 and 1!")
        return v


class SimilarProductDetails(BaseModel):
    product_id: str
    name: str
    main_category: str
    sub_category: str
    image_url: str
    ratings: float
    discount_price: float
    actual_price: float
    modified_date: datetime
    created_date: datetime
    score: float

    @field_validator("score")
    def score_must_within_range(cls, v):
        if v < -1 or v > 1:
            raise ValueError("score must be between -1 and 1")
        return v


class SimilarProductsResponseModel(BaseModel):
    similar_products: list[SimilarProductDetails]
    query: str
    created_date: datetime
    modified_date: datetime
