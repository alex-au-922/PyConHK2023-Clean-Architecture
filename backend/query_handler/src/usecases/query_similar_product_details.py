from abc import abstractmethod, ABC
from entities import EmbeddedQueryDetails
from typing import Optional, overload, Sequence


class QuerySimilarProductDetailsUseCase(ABC):
    @overload
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails,
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]]:
        ...

    @overload
    def query(
        self,
        embedded_query_details: Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> list[Optional[list[tuple[str, float]]]]:
        ...

    @abstractmethod
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails | Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]] | list[Optional[list[tuple[str, float]]]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
