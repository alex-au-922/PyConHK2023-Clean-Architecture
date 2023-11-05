from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EmbeddedProductDetails:
    product_id: str
    embedding: list[float]
    modified_date: datetime
    created_date: datetime
