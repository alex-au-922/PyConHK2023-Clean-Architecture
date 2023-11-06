from contextlib import contextmanager
from usecases import QuerySimilarProductDetailsUseCase
from entities import EmbeddedQueryDetails
import psycopg2
from psycopg2.extensions import connection
from typing import Optional, Sequence, overload, TypeVar, Iterator
from typing_extensions import override
import logging

T = TypeVar("T")


class PostgresQuerySimilarProductDetailsClient(QuerySimilarProductDetailsUseCase):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        embedded_product_table_name: str,
        default_threshold: float,
        default_top_k: int,
        fetch_batch_size: int,
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database = database
        self._embedded_product_table_name = embedded_product_table_name
        self._default_threshold = default_threshold
        self._default_top_k = default_top_k
        self._fetch_batch_size = fetch_batch_size
        self._conn: Optional[connection] = None

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

    @contextmanager
    def _get_conn(self) -> Iterator[connection]:
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(
                database=self._database,
                user=self._username,
                password=self._password,
                host=self._host,
                port=self._port,
            )
        yield self._conn

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
            with self._get_conn() as conn, conn.cursor() as cursor:
                try:
                    stmt = """
                        SELECT
                            product_id,
                            (embedding <#> %(embedding)s::vector) * -1 AS score
                        FROM {table_name}
                            WHERE (embedding <#> %(embedding)s::vector) * -1 <= %(threshold)s
                            ORDER BY (embedding <#> %(embedding)s::vector) * -1 DESC
                        LIMIT %(top_k)s
                        """.format(
                        table_name=self._embedded_product_table_name,
                    )
                    cursor.execute(
                        stmt,
                        {
                            "embedding": embedded_query_details.embedding,
                            "top_k": self._get_top_k(top_k),
                            "threshold": self._get_threshold(threshold),
                        },
                    )
                    return [
                        (product_id, float(score))
                        for product_id, score in cursor.fetchall()
                    ]
                except Exception as e:
                    logging.exception(e)
                    logging.error("Error fetching product details from Postgres!")
                    conn.rollback()
                    return None
        except Exception as e:
            logging.exception(e)
            logging.error("Error getting Postgres connection!")
            return None

    def _query_many(
        self,
        embedded_query_details_list: Sequence[EmbeddedQueryDetails],
        threshold: Optional[float],
        top_k: Optional[int],
    ) -> Optional[list[tuple[str, float]]]:
        """Fetch a batch of product details from the database"""

        similar_products_results: list[Optional[list[tuple[str, float]]]] = []
        for embedded_query_details_batch in self._batch_generator(
            embedded_query_details_list, self._fetch_batch_size
        ):
            try:
                with self._get_conn() as conn, conn.cursor() as cursor:
                    try:
                        stmt = """
                            SELECT
                                product_id,
                                (embedding <#> %(embedding)s::vector) * -1 AS score
                            FROM {table_name}
                                WHERE (embedding <#> %(embedding)s::vector) * -1 <= %(threshold)s
                                ORDER BY (embedding <#> %(embedding)s::vector) * -1 DESC
                            LIMIT %(top_k)s""".format(
                            table_name=self._embedded_product_table_name
                        )
                        cursor.executemany(
                            stmt,
                            [
                                {
                                    "embedding": embedded_query_details.embedding,
                                    "top_k": self._get_top_k(top_k),
                                    "threshold": self._get_threshold(threshold),
                                }
                                for embedded_query_details in embedded_query_details_batch
                            ],
                        )
                        result = cursor.fetchall()
                        similar_products_results.extend(
                            [
                                [
                                    (product_id, float(score))
                                    for product_id, score in result_batch
                                ]
                                for result_batch in result
                            ]
                        )
                    except Exception as e:
                        logging.exception(e)
                        logging.error("Error fetching product details from Postgres!")
                        conn.rollback()
                        similar_products_results.extend(
                            [None] * len(embedded_query_details_batch)
                        )
            except Exception as e:
                logging.exception(e)
                logging.error("Error getting Postgres connection!")
                similar_products_results.extend(
                    [None] * len(embedded_query_details_batch)
                )
        return similar_products_results

    @override
    def close(self) -> bool:
        try:
            if self._conn is None:
                return True
            self._conn.close()
            return True
        except Exception as e:
            logging.exception(e)
            logging.error("Error closing Postgres connection!")
            return False
