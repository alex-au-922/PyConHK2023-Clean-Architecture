from abc import abstractmethod, ABC
from entities import RawProductDetails, EmbeddedProductDetails
from typing import Optional, overload, Sequence


class EmbedRawProductDetailsUseCase(ABC):
    @overload
    def embed(
        self, raw_product_details: RawProductDetails
    ) -> Optional[EmbeddedProductDetails]:
        ...

    @overload
    def embed(
        self, raw_product_details: Sequence[RawProductDetails]
    ) -> list[Optional[EmbeddedProductDetails]]:
        ...

    @abstractmethod
    def embed(
        self, raw_product_details: RawProductDetails | Sequence[RawProductDetails]
    ) -> Optional[EmbeddedProductDetails] | list[Optional[EmbeddedProductDetails]]:
        ...

    @abstractmethod
    def close(self) -> bool:
        ...
