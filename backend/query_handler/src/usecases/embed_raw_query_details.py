from abc import abstractmethod, ABC
from entities import RawQueryDetails, EmbeddedQueryDetails
from typing import Optional, overload


class EmbedRawQueryDetailsUseCase(ABC):
    @overload
    def embed(
        self, raw_query_details: RawQueryDetails
    ) -> Optional[EmbeddedQueryDetails]:
        ...

    @overload
    def embed(
        self, raw_query_details: list[RawQueryDetails]
    ) -> list[Optional[EmbeddedQueryDetails]]:
        ...

    @abstractmethod
    def embed(
        self, raw_product_details: RawQueryDetails | list[RawQueryDetails]
    ) -> Optional[EmbeddedQueryDetails] | list[Optional[EmbeddedQueryDetails]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
