from datetime import datetime
from usecases import EmbedRawQueryDetailsUseCase
from entities import RawQueryDetails, EmbeddedQueryDetails
from typing import Optional, overload, Sequence
from typing_extensions import override
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
import numpy.typing as npt
import numpy as np


class OnnxEmbedRawQueryDetailsClient(EmbedRawQueryDetailsUseCase):
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
        self, raw_query_details: RawQueryDetails
    ) -> Optional[EmbeddedQueryDetails]:
        ...

    @overload
    def embed(
        self, raw_query_details: Sequence[RawQueryDetails]
    ) -> list[Optional[EmbeddedQueryDetails]]:
        ...

    @override
    def embed(
        self, raw_query_details: RawQueryDetails | Sequence[RawQueryDetails]
    ) -> Optional[EmbeddedQueryDetails] | list[Optional[EmbeddedQueryDetails]]:
        if isinstance(raw_query_details, RawQueryDetails):
            return self._embed_single(raw_query_details)
        return [
            self._embed_single(raw_query_detail)
            for raw_query_detail in raw_query_details
        ]

    def _embed_single(self, raw_query_details: RawQueryDetails) -> EmbeddedQueryDetails:
        """Embed a single RawProductDetails"""

        tokenized_input: dict[str, npt.NDArray[np.float_]] = dict(
            self._tokenizer(
                [raw_query_details.query.lower()],
                return_tensors="np",
                padding=True,
                truncation=True,
            )
        )

        embedding: npt.NDArray[np.float_] = self._inference_session.run(
            ["output"], tokenized_input
        )[0][0]

        return EmbeddedQueryDetails(
            embedding=embedding.tolist(),
            created_date=datetime.now(),
        )

    @override
    def close(self) -> bool:
        return True
