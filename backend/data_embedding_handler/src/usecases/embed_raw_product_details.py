from abc import abstractmethod, ABC
from entities import RawProductDetails, EmbeddedProductDetails
from typing import Optional, overload


class EmbedRawProductDetailsUseCase(ABC):
    @overload
    def embed(
        self, raw_product_details: RawProductDetails
    ) -> Optional[EmbeddedProductDetails]:
        ...

    @overload
    def embed(
        self, raw_product_details: list[RawProductDetails]
    ) -> list[Optional[EmbeddedProductDetails]]:
        ...

    @abstractmethod
    def embed(
        self, raw_product_details: RawProductDetails | list[RawProductDetails]
    ) -> Optional[EmbeddedProductDetails] | list[Optional[EmbeddedProductDetails]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
