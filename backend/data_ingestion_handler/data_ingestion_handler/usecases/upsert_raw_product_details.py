from abc import abstractmethod, ABC
from entities import RawProductDetails
from typing import overload, Sequence


class UpsertRawProductDetailsUseCase(ABC):
    @overload
    def upsert(self, raw_product_details: RawProductDetails) -> bool:
        ...

    @overload
    def upsert(self, raw_product_details: Sequence[RawProductDetails]) -> list[bool]:
        ...

    @abstractmethod
    def upsert(
        self, raw_product_details: RawProductDetails | Sequence[RawProductDetails]
    ) -> bool | list[bool]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
