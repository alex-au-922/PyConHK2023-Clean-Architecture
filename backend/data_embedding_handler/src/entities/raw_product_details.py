from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawProductDetails:
    product_id: str
    name: str
    modified_date: datetime
