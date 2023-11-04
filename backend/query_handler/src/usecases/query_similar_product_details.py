from abc import abstractmethod, ABC
from entities import EmbeddedQueryDetails
from typing import Optional, overload


class QuerySimilarProductDetailsUseCase(ABC):
    @overload
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails,
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> list[str]:
        ...

    @overload
    def query(
        self,
        embedded_query_details: list[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> list[list[str]]:
        ...

    @abstractmethod
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails | list[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> list[str] | list[list[str]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
