from datetime import datetime
from usecases import UpsertEmbeddedProductDetailsUseCase
from entities import EmbeddedProductDetails
from opensearchpy import (
    OpenSearch,
    RequestsHttpConnection,
    AWSV4SignerAuth,
    helpers as opensearch_helpers,
    ConflictError,
)
from typing import ClassVar, Optional, Sequence, overload, TypeVar, Iterator
from typing_extensions import override
import logging

T = TypeVar("T")


class OpenSearchUpsertEmbeddedProductDetailsClient(UpsertEmbeddedProductDetailsUseCase):
    _allowed_error_codes: ClassVar[tuple[int, ...]] = (409,)

    def __init__(
        self,
        opensearch_endpoint: str,
        index_name: str,
        master_auth: AWSV4SignerAuth | tuple[str, str],
        upsert_batch_size: int,
        timeout: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._client = OpenSearch(
            hosts=opensearch_endpoint,
            http_auth=master_auth,
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection,
            timeout=timeout,
        )
        self._index_name = index_name
        self._upsert_batch_size = upsert_batch_size

    @overload
    def upsert(self, embedded_product_details: EmbeddedProductDetails) -> bool:
        ...

    @overload
    def upsert(
        self, embedded_product_details: Sequence[EmbeddedProductDetails]
    ) -> list[bool]:
        ...

    @override
    def upsert(
        self,
        embedded_product_details: EmbeddedProductDetails
        | Sequence[EmbeddedProductDetails],
    ) -> bool | list[bool]:
        if isinstance(embedded_product_details, EmbeddedProductDetails):
            return self._upsert_single(embedded_product_details)
        return self._upsert_batch(embedded_product_details)

    def _serialize_embedded_product_details(
        self, embedded_product_details: EmbeddedProductDetails
    ) -> dict:
        """Serialize product details into opensearch format"""

        return {
            "product_id": embedded_product_details.product_id,
            "product_embedding": embedded_product_details.embedding,
            "modified_date": datetime.strftime(
                embedded_product_details.modified_date,
                "%Y-%m-%d %H:%M:%S",
            ),
            "created_date": datetime.strftime(
                embedded_product_details.created_date,
                "%Y-%m-%d %H:%M:%S",
            ),
        }

    def _get_product_details_modified_micro_timestamp(
        self, embedded_product_details: EmbeddedProductDetails
    ) -> int:
        """Get the modified timestamp of the product details in microseconds"""

        return int(embedded_product_details.modified_date.timestamp() * 1e6)

    def _batch_generator(
        self, data: Sequence[T], batch_size: int
    ) -> Iterator[Sequence[T]]:
        """Separate sequence of data into several batches based on batch sizes"""

        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def _upsert_single(self, embedded_product_details: EmbeddedProductDetails) -> bool:
        """Upsert a single embedded product to OpenSearch. Ignore Conflict Error"""

        try:
            self._client.index(
                index=self._index_name,
                body=self._serialize_embedded_product_details(embedded_product_details),
                id=embedded_product_details.product_id,
                #! We can make use of the microsecond timestamp of the modified
                #! date of the product details as the version of the document,
                #! so we can avoid the error of race conditions when upserting in
                #! OpenSearch, check: https://opensearch.org/docs/latest/api-reference/document-apis/index-document/
                version=self._get_product_details_modified_micro_timestamp(
                    embedded_product_details
                ),
                version_type="external_gte",
            )
            return True
        except ConflictError:
            logging.info(
                f"Newer version of document {embedded_product_details.product_id} already exists!"
            )
            return True
        except Exception:
            logging.exception(
                f"Error upserting document {embedded_product_details.product_id}!"
            )
            return False

    def _upsert_batch(
        self, embedded_product_details: Sequence[EmbeddedProductDetails]
    ) -> list[bool]:
        """Upsert a batch of embedded product details to OpenSearch. Ignore Conflict Error"""

        successes: list[bool] = []
        for embedded_products_batch in self._batch_generator(
            embedded_product_details, self._upsert_batch_size
        ):
            try:
                batch_successes_map: dict[str, bool] = {
                    embedded_product_details.product_id: True
                    for embedded_product_details in embedded_products_batch
                }

                bulk_index_result = opensearch_helpers.bulk(
                    self._client,
                    [
                        {
                            "_op_type": "index",
                            "_index": self._index_name,
                            "_id": embedded_product_details.product_id,
                            #! We can make use of the microsecond timestamp of the modified
                            #! date of the product details as the version of the document,
                            #! OpenSearch, check: https://opensearch.org/docs/latest/api-reference/document-apis/index-document/
                            #! so we can avoid the error of race conditions when upserting in
                            "_version": self._get_product_details_modified_micro_timestamp(
                                embedded_product_details
                            ),
                            "_version_type": "external_gte",
                            "_source": self._serialize_embedded_product_details(
                                embedded_product_details
                            ),
                        }
                        for embedded_product_details in embedded_products_batch
                    ],
                    raise_on_error=False,
                )
                failed_product_ids: list[str] = []

                for index_error in bulk_index_result[1]:
                    error_id = index_error["index"]["_id"]
                    error_status = index_error["index"]["status"]
                    error_type = index_error["index"]["error"]["type"]
                    error_reason = index_error["index"]["error"]["reason"]
                    error_msg = f"{error_type} {error_reason}"
                    if error_status in self._allowed_error_codes:
                        logging.info(
                            f"Newer version of document {embedded_product_details.product_id} already exists!"
                        )
                    else:
                        logging.error(error_msg)
                        batch_successes_map[error_id] = False
                        failed_product_ids.append(error_id)

                successes.extend(
                    [
                        batch_successes_map[embedded_product_details.product_id]
                        for embedded_product_details in embedded_products_batch
                    ]
                )

                if failed_product_ids:
                    logging.error(
                        f"Failed to upsert products {failed_product_ids} to opensearch"
                    )

            except Exception:
                failed_product_ids = [
                    embedded_product_details.product_id
                    for embedded_product_details in embedded_products_batch
                ]
                logging.exception(
                    f"Failed to upsert jobs {failed_product_ids} to opensearch"
                )
                successes.extend([False] * (len(embedded_products_batch)))
        return successes

    @override
    def close(self) -> bool:
        try:
            self._client.close()
            return True
        except Exception:
            logging.exception("Error closing opensearch client!")
            return False
