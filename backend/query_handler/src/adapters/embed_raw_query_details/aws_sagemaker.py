from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import logging
from usecases import EmbedRawQueryDetailsUseCase
from entities import RawQueryDetails, EmbeddedQueryDetails
from typing import ClassVar, Iterator, Optional, overload, Sequence, TypeVar
from typing_extensions import override
from typing import Callable
from mypy_boto3_sagemaker_runtime import SageMakerRuntimeClient

T = TypeVar("T")


class AWSSageMakerEmbedRawQueryDetailsClient(EmbedRawQueryDetailsUseCase):
    _client_revoke_timeout: ClassVar[int] = 30 * 60  # 30 minutes

    def __init__(
        self,
        client_creator: Callable[[], SageMakerRuntimeClient],
        endpoint_name: str,
        embed_batch_size: int,
    ) -> None:
        super().__init__()
        self._client_creator = client_creator
        self._endpoint_name = endpoint_name
        self._embed_batch_size = embed_batch_size
        self._client: SageMakerRuntimeClient = self._client_creator()
        self._last_revoke_time: datetime = datetime.now()

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
        return self._embed_batch(raw_query_details)

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
        self, raw_query_details: RawQueryDetails
    ) -> Optional[EmbeddedQueryDetails]:
        """Embed a single RawProductDetails"""
        try:
            with self._get_client() as client:
                embedding: list[float] = json.loads(
                    client.invoke_endpoint(
                        EndpointName=self._endpoint_name,
                        Body=json.dumps({"text": raw_query_details.query.lower()}),
                    )["Body"]
                    .read()
                    .decode("utf-8")
                )["result"]

                return EmbeddedQueryDetails(
                    embedding=embedding,
                    created_date=datetime.now(),
                )
        except Exception as e:
            logging.exception(e)
            logging.error(f"Error embedding query {raw_query_details.query}!")
            return None

    def _embed_batch(
        self, raw_query_details: Sequence[RawQueryDetails]
    ) -> list[Optional[EmbeddedQueryDetails]]:
        embedded_query_details_list: list[Optional[EmbeddedQueryDetails]] = []

        for batch in self._batch_generator(raw_query_details, self._embed_batch_size):
            with ThreadPoolExecutor(max_workers=10) as executor:
                embedded_query_details_list.extend(
                    executor.map(self._embed_single, batch)
                )
        return embedded_query_details_list

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
