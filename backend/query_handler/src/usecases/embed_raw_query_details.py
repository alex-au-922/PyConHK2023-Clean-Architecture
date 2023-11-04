from abc import abstractmethod, ABC
from entities import RawQueryDetails, EmbeddedQueryDetails
from typing import Optional, overload, Sequence


class EmbedRawQueryDetailsUseCase(ABC):
    @overload
    def embed(
        self, raw_query_details: RawQueryDetails
    ) -> Optional[EmbeddedQueryDetails]:
        ...

    @overload
    def embed(
        self, raw_query_details: Sequence[RawQueryDetails]
    ) -> list[Optional[EmbeddedQueryDetails]]:
        ...

    @abstractmethod
    def embed(
        self, raw_query_details: RawQueryDetails | Sequence[RawQueryDetails]
    ) -> Optional[EmbeddedQueryDetails] | list[Optional[EmbeddedQueryDetails]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
