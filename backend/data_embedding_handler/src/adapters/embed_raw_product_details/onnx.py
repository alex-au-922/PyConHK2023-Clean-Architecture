from datetime import datetime
from usecases import EmbedRawProductDetailsUseCase
from entities import RawProductDetails, EmbeddedProductDetails
from typing import Optional, overload, Sequence
from typing_extensions import override
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
import numpy.typing as npt
import numpy as np


class OnnxEmbedRawProductDetailsClient(EmbedRawProductDetailsUseCase):
    def __init__(
        self,
        inference_session: InferenceSession,
        tokenizer: AutoTokenizer,
    ) -> None:
        super().__init__()
        self._inference_session = inference_session
        self._tokenizer = tokenizer

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

    @override
    def embed(
        self, raw_product_details: RawProductDetails | Sequence[RawProductDetails]
    ) -> Optional[EmbeddedProductDetails] | list[Optional[EmbeddedProductDetails]]:
        if isinstance(raw_product_details, Sequence):
            return [
                self._embed_single(raw_product_detail)
                for raw_product_detail in raw_product_details
            ]
        return self._embed_single(raw_product_details)

    def _embed_single(
        self, raw_product_details: RawProductDetails
    ) -> EmbeddedProductDetails:
        """Embed a single RawProductDetails"""

        tokenized_input: dict[str, npt.NDArray[np.float_]] = dict(
            self._tokenizer(
                [raw_product_details.name],
                return_tensors="np",
                padding=True,
                truncation=True,
            )
        )

        embedding: npt.NDArray[np.float_] = self._inference_session.run(
            ["output"], tokenized_input
        )[0][0]

        return EmbeddedProductDetails(
            product_id=raw_product_details.product_id,
            embedding=embedding.tolist(),
            modified_date=raw_product_details.modified_date,
            created_date=datetime.now(),
        )

    @override
    def close(self) -> bool:
        return True
