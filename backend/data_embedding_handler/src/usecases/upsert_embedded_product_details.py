from abc import abstractmethod, ABC
from entities import EmbeddedProductDetails
from typing import overload, Sequence


class UpsertEmbeddedProductDetailsUseCase(ABC):
    @overload
    def upsert(self, embedded_product_details: EmbeddedProductDetails) -> bool:
        ...

    @overload
    def upsert(
        self, embedded_product_details: Sequence[EmbeddedProductDetails]
    ) -> list[bool]:
        ...

    @abstractmethod
    def upsert(
        self,
        embedded_product_details: EmbeddedProductDetails
        | Sequence[EmbeddedProductDetails],
    ) -> bool | list[bool]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
