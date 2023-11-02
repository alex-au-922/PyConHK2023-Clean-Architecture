from contextlib import contextmanager
from datetime import datetime, timedelta
import json
from usecases import UpsertRawProductDetailsUseCase
from entities import RawProductDetails
from typing import ClassVar, Sequence, overload, TypeVar, Iterator, Callable
from typing_extensions import override
from mypy_boto3_sqs import SQSClient
import logging

T = TypeVar("T")


class AWSSQSUpsertRawProductDetailsClient(UpsertRawProductDetailsUseCase):
    _success_status_codes: ClassVar[tuple[int, ...]] = (200, 202, 204)
    _client_revoke_timeout: ClassVar[int] = 30 * 60  # 30 minutes

    def __init__(
        self,
        client_creator: Callable[[], SQSClient],
        queue_url: str,
        upsert_batch_size: int,
    ) -> None:
        super().__init__()
        self._client_creator = client_creator
        self._queue_url = queue_url
        self._upsert_batch_size = upsert_batch_size
        self._client = self._client_creator()
        self._last_revoke_time = datetime.now()

    @overload
    def upsert(self, raw_product_details: RawProductDetails) -> bool:
        ...

    @overload
    def upsert(self, raw_product_details: Sequence[RawProductDetails]) -> list[bool]:
        ...

    @override
    def upsert(
        self, raw_product_details: RawProductDetails | Sequence[RawProductDetails]
    ) -> bool | list[bool]:
        if isinstance(raw_product_details, RawProductDetails):
            return self._upsert_single(raw_product_details)
        return self._upsert_batch(raw_product_details)

    def _serialize_raw_product_details(
        self, raw_product_details: RawProductDetails
    ) -> dict:
        """Serialize raw product details to JSON string"""
        return {
            "product_id": raw_product_details.product_id,
            "modified_date": datetime.strftime(
                raw_product_details.modified_date, "%Y-%m-%d %H:%M:%S.%f"
            ),
        }

    @contextmanager
    def _get_client(self) -> Iterator[SQSClient]:
        """Get SQS client and revoke after use"""

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

    def _upsert_single(self, raw_product_details: RawProductDetails) -> bool:
        """Upsert a single raw product id to SQS."""
        try:
            with self._get_client() as client:
                response = client.send_message(
                    QueueUrl=self._queue_url,
                    MessageBody=self._serialize_raw_product_details(
                        raw_product_details
                    ),
                )
                if (
                    response["ResponseMetadata"]["HTTPStatusCode"]
                    not in self._success_status_codes
                ):
                    raise Exception(
                        f"Found error status code {response['ResponseMetadata']['HTTPStatusCode']}!"
                    )
                return True
        except Exception:
            logging.exception(
                f"Error upserting raw product details {raw_product_details.product_id}!"
            )
            return False

    def _upsert_batch(
        self, raw_product_details: Sequence[RawProductDetails]
    ) -> list[bool]:
        """Upsert a batch of raw products ids to SQS."""
        successes: list[bool] = []
        for raw_products_batch in self._batch_generator(
            raw_product_details, self._upsert_batch_size
        ):
            try:
                with self._get_client() as client:
                    response = client.send_message_batch(
                        QueueUrl=self._queue_url,
                        Entries=[
                            {
                                "Id": raw_product_detail.product_id,
                                "MessageBody": json.dumps(
                                    self._serialize_raw_product_details(
                                        raw_product_detail
                                    )
                                ),
                            }
                            for raw_product_detail in raw_products_batch
                        ],
                    )
                    if (
                        response["ResponseMetadata"]["HTTPStatusCode"]
                        not in self._success_status_codes
                    ):
                        raise Exception(
                            f"Found error status code {response['ResponseMetadata']['HTTPStatusCode']}!"
                        )
                    successes.extend([True] * len(raw_products_batch))
            except Exception:
                failed_product_ids = [
                    raw_product_detail.product_id
                    for raw_product_detail in raw_products_batch
                ]
                logging.exception(
                    f"Error upserting raw product details {','.join(failed_product_ids)}!"
                )
                successes.extend([False] * len(raw_products_batch))
        return successes

    @override
    def close(self) -> bool:
        try:
            if self._client is None:
                return True
            self._client.close()
            return True
        except Exception:
            logging.exception("Error closing SQS client!")
            return False
