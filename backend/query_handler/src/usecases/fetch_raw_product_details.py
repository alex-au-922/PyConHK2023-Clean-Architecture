from abc import abstractmethod, ABC
from entities import RawProductDetails
from typing import Optional, overload, Sequence


class FetchRawProductDetailsUseCase(ABC):
    @overload
    def fetch(self, product_id: str) -> Optional[RawProductDetails]:
        ...

    @overload
    def fetch(self, product_id: Sequence[str]) -> list[Optional[RawProductDetails]]:
        ...

    @abstractmethod
    def fetch(
        self, product_id: str | Sequence[str]
    ) -> Optional[RawProductDetails] | list[Optional[RawProductDetails]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
