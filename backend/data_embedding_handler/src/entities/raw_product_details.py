from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RawProductDetails:
    product_id: str
    name: str
    modified_date: datetime
