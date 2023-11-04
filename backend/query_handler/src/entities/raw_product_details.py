from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RawProductDetails:
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
