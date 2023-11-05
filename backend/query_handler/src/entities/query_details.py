from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RawQueryDetails:
    query: str
    created_date: datetime


@dataclass(frozen=True, slots=True)
class EmbeddedQueryDetails:
    embedding: list[float]
    created_date: datetime
