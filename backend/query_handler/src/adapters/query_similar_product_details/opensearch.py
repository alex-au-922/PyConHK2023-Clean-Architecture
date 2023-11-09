from concurrent.futures import ThreadPoolExecutor
from usecases import QuerySimilarProductDetailsUseCase
from entities import EmbeddedQueryDetails
from opensearchpy import (
    OpenSearch,
    RequestsHttpConnection,
    AWSV4SignerAuth,
)
from typing import Optional, Sequence, overload, TypeVar, Iterator
from typing_extensions import override
import logging

T = TypeVar("T")


class OpenSearchQuerySimilarProductDetailsClient(QuerySimilarProductDetailsUseCase):
    def __init__(
        self,
        opensearch_endpoint: str,
        index_name: str,
        master_auth: AWSV4SignerAuth | tuple[str, str],
        default_threshold: float,
        default_top_k: int,
        fetch_batch_size: int,
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
        self._default_threshold = default_threshold
        self._default_top_k = default_top_k
        self._fetch_batch_size = fetch_batch_size

    @overload
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails,
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]]:
        ...

    @overload
    def query(
        self,
        embedded_query_details: Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> list[Optional[list[tuple[str, float]]]]:
        ...

    @override
    def query(
        self,
        embedded_query_details: EmbeddedQueryDetails | Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]] | list[Optional[list[tuple[str, float]]]]:
        if isinstance(embedded_query_details, EmbeddedQueryDetails):
            return self._query_single(embedded_query_details, threshold, top_k)
        return self._query_many(embedded_query_details, threshold, top_k)

    def _get_threshold(self, threshold: Optional[float]) -> float:
        """Get threshold from input or default threshold"""
        if threshold is None:
            return self._default_threshold
        return threshold

    def _get_top_k(self, top_k: Optional[int]) -> int:
        """Get top_k from input or default top_k"""
        if top_k is None:
            return self._default_top_k
        return top_k

    def _batch_generator(
        self, data: Sequence[T], batch_size: int
    ) -> Iterator[Sequence[T]]:
        """Separate sequence of data into several batches based on batch sizes"""

        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def _query_single(
        self,
        embedded_query_details: EmbeddedQueryDetails,
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]]:
        """Query a similar product details based on threshold and top_k from the database"""
        try:
            query = {
                "size": self._get_top_k(top_k),
                "query": {
                    "knn": {
                        "product_embedding": {
                            "vector": embedded_query_details.embedding,
                            "k": self._get_top_k(top_k),
                        }
                    }
                },
                #! Check https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/ for the score calculation
                #! For the min_score, we have to convert from cosine similarity to the formula below
                "min_score": (1 + self._get_threshold(threshold)) / 2,
            }

            result = self._client.search(
                index=self._index_name,
                body=query,
                _source_includes=["product_id"],
            )

            return [
                #! Check https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/ for the score calculation
                #! 3 - 2 * hit["_score"] is the cosine similarity according to opensearch
                (hit["_source"]["product_id"], 3 - 2 * hit["_score"])
                for hit in result["hits"]["hits"]
            ]
        except Exception as e:
            logging.exception(e)
            logging.error("Error getting OpenSearch connection!")
            return None

    def _query_many(
        self,
        embedded_query_details_list: Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]]:
        """Fetch a batch of product details from the database"""

        similar_products_results: list[Optional[list[tuple[str, float]]]] = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for embedded_query_details_batch in self._batch_generator(
                embedded_query_details_list, self._fetch_batch_size
            ):
                try:
                    similar_products_results.extend(
                        executor.map(
                            self._query_single,
                            embedded_query_details_batch,
                            [threshold] * len(embedded_query_details_batch),
                            [top_k] * len(embedded_query_details_batch),
                        )
                    )
                except Exception as e:
                    logging.exception(e)
                    logging.error("Error getting OpenSearch connection!")
                    similar_products_results.extend(
                        [None] * len(embedded_query_details_batch)
                    )
        return similar_products_results

    @override
    def close(self) -> bool:
        try:
            self._client.close()
            return True
        except Exception as e:
            logging.exception(e)
            logging.error("Error closing opensearch client!")
            return False
