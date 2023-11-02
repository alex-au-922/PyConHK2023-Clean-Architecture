from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import logging
from usecases import EmbedRawProductDetailsUseCase
from entities import RawProductDetails, EmbeddedProductDetails
from typing import ClassVar, Iterator, Optional, overload, Sequence, TypeVar
from typing_extensions import override
from transformers import AutoTokenizer
from typing import Callable
from mypy_boto3_sagemaker_runtime import SageMakerRuntimeClient
import numpy.typing as npt
import numpy as np

T = TypeVar("T")


class AWSSageMakerEmbedRawProductDetailsClient(EmbedRawProductDetailsUseCase):
    _client_revoke_timeout: ClassVar[int] = 30 * 60  # 30 minutes

    def __init__(
        self,
        client_creator: Callable[[], SageMakerRuntimeClient],
        endpoint_name: str,
        tokenizer: AutoTokenizer,
        embed_batch_size: int,
    ) -> None:
        super().__init__()
        self._client_creator = client_creator
        self._endpoint_name = endpoint_name
        self._tokenizer = tokenizer
        self._embed_batch_size = embed_batch_size
        self._client: SageMakerRuntimeClient = self._client_creator()
        self._last_revoke_time: datetime = datetime.now()

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
        if isinstance(raw_product_details, RawProductDetails):
            return self._embed_single(raw_product_details)
        return self._embed_batch(raw_product_details)

    @contextmanager
    def _get_client(self) -> Iterator[SageMakerRuntimeClient]:
        """Get SageMaker client and revoke after use"""

        if (
            datetime.now() - timedelta(seconds=self._client_revoke_timeout)
        ) > self._last_revoke_time:
            self._client = self._client_creator()
            self._last_revoke_time = datetime.now()
        yield self._client

    def _batch_generator(
        self, data: Sequence[T], batch_size: int
    ) -> Iterator[Sequence[T]]:
        """Separate sequence of data into several batches based on batch sizes"""

        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def _embed_single(
        self, raw_product_details: RawProductDetails
    ) -> Optional[EmbeddedProductDetails]:
        """Embed a single RawProductDetails"""
        try:
            with self._get_client() as client:
                tokenized_input: dict[str, npt.NDArray[np.float_]] = dict(
                    self._tokenizer(
                        [raw_product_details.name],
                        return_tensors="np",
                        padding=True,
                        truncation=True,
                    )
                )

                embedding: list[float] = json.loads(
                    client.invoke_endpoint(
                        EndpointName="text-embeddings",
                        Body=tokenized_input,
                    )["Body"]
                    .read()
                    .decode("utf-8")
                )

                return EmbeddedProductDetails(
                    product_id=raw_product_details.product_id,
                    embedding=embedding,
                    modified_date=raw_product_details.modified_date,
                    created_date=datetime.now(),
                )
        except Exception as e:
            logging.exception(e)
            logging.error(f"Error embedding product {raw_product_details.product_id}!")
            return None

    def _embed_batch(
        self, raw_product_details: Sequence[RawProductDetails]
    ) -> list[EmbeddedProductDetails]:
        embedded_product_details: list[EmbeddedProductDetails] = []

        for batch in self._batch_generator(raw_product_details, self._embed_batch_size):
            try:
                with self._get_client() as client:
                    tokenized_input: dict[str, npt.NDArray[np.float_]] = dict(
                        self._tokenizer(
                            [raw_product_detail.name for raw_product_detail in batch],
                            return_tensors="np",
                            padding=True,
                            truncation=True,
                        )
                    )

                    embeddings: list[list[float]] = json.loads(
                        client.invoke_endpoint(
                            EndpointName="text-embeddings",
                            Body=tokenized_input,
                        )["Body"]
                        .read()
                        .decode("utf-8")
                    )

                    embedded_product_details.extend(
                        [
                            EmbeddedProductDetails(
                                product_id=raw_product_detail.product_id,
                                embedding=embedding,
                                modified_date=raw_product_detail.modified_date,
                                created_date=datetime.now(),
                            )
                            for raw_product_detail, embedding in zip(batch, embeddings)
                        ]
                    )
            except Exception as e:
                failed_product_ids = [
                    raw_product_detail.product_id for raw_product_detail in batch
                ]
                logging.exception(e)
                logging.error(
                    f"Error embedding products {','.join(failed_product_ids)}!"
                )
                embedded_product_details.extend([None] * len(batch))
        return embedded_product_details

    @override
    def close(self) -> bool:
        try:
            if self._client is None:
                return True
            self._client.close()
            return True
        except Exception as e:
            logging.exception(e)
            logging.error("Error closing SageMaker client!")
            return False
