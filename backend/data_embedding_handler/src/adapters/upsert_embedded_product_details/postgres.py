from contextlib import contextmanager
from usecases import UpsertEmbeddedProductDetailsUseCase
from entities import EmbeddedProductDetails
import psycopg
from typing import Optional, Sequence, overload, TypeVar, Iterator
from typing_extensions import override
import logging

T = TypeVar("T")


class PostgresUpsertEmbeddedProductDetailsClient(UpsertEmbeddedProductDetailsUseCase):
    def __init__(
        self,
        connection_string: str,
        embedded_product_table_name: str,
        upsert_batch_size: int,
    ) -> None:
        super().__init__()
        self._connection_string = connection_string
        self._embedded_product_table_name = embedded_product_table_name
        self._upsert_batch_size = upsert_batch_size
        self._conn: Optional[psycopg.Connection] = None

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
        if isinstance(embedded_product_details, Sequence):
            return self._upsert_batch(embedded_product_details)
        return self._upsert_single(embedded_product_details)

    def _embedded_product_details_to_sql_tuple(
        self, embedded_product_details: EmbeddedProductDetails
    ) -> tuple:
        """Serialize EmbeddedProductDetails to tuple for SQL insertion"""
        return (
            embedded_product_details.product_id,
            embedded_product_details.embedding,
            embedded_product_details.modified_date,
            embedded_product_details.created_date,
        )

    @contextmanager
    def _get_conn(self) -> Iterator[psycopg.Connection]:
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(self._connection_string)
        yield self._conn

    def _batch_generator(
        self, data: Sequence[T], batch_size: int
    ) -> Iterator[Sequence[T]]:
        """Separate sequence of data into several batches based on batch sizes"""

        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def _upsert_single(self, embedded_product_details: EmbeddedProductDetails) -> bool:
        """Upsert a single embedded product to Postgres."""

        try:
            with self._get_conn() as conn, conn.cursor() as cur:
                stmt = """
                    INSERT INTO {table_name} (
                        product_id,
                        product_embedding,
                        modified_date,
                        created_date
                    ) VALUES (
                        %s, %s, %s, %s
                    ) ON CONFLICT (product_id) DO UPDATE SET
                        product_embedding = EXCLUDED.product_embedding,
                        modified_date = EXCLUDED.modified_date
                        created_date = EXCLUDED.created_date
                    WHEN EXCLUDED.modified_date > {table_name}.modified_date
                """.format(
                    table_name=self._embedded_product_table_name
                )

                cur.execute(
                    stmt,
                    self._embedded_product_details_to_sql_tuple(
                        embedded_product_details
                    ),
                )
                conn.commit()
                return True
        except Exception:
            logging.exception(
                f"Error upserting embedded product details {embedded_product_details.product_id}!"
            )
            return False

    def _upsert_batch(
        self, embedded_product_details: Sequence[EmbeddedProductDetails]
    ) -> list[bool]:
        """Upsert a batch of embedded products to Postgres."""
        successes: list[bool] = []
        for embedded_products_batch in self._batch_generator(
            embedded_product_details, self._upsert_batch_size
        ):
            try:
                with self._get_conn() as conn, conn.cursor() as cur:
                    stmt = """
                        INSERT INTO {table_name} (
                            product_id,
                            product_embedding,
                            modified_date,
                            created_date
                        ) VALUES (
                            %s, %s, %s, %s
                        ) ON CONFLICT (product_id) DO UPDATE SET
                            product_embedding = EXCLUDED.product_embedding,
                            modified_date = EXCLUDED.modified_date
                            created_date = EXCLUDED.created_date
                        WHEN EXCLUDED.modified_date > {table_name}.modified_date
                    """.format(
                        table_name=self._embedded_product_table_name
                    )

                    cur.executemany(
                        stmt,
                        [
                            self._embedded_product_details_to_sql_tuple(
                                embedded_product_detail
                            )
                            for embedded_product_detail in embedded_products_batch
                        ],
                    )
                    conn.commit()
                    successes.extend([True] * len(embedded_products_batch))
            except Exception as e:
                failed_product_ids = [
                    embedded_product_detail.product_id
                    for embedded_product_detail in embedded_products_batch
                ]
                logging.exception(
                    f"Error upserting embedded product details {','.join(failed_product_ids)}!"
                )
                successes.extend([False] * len(embedded_products_batch))
        return successes

    @override
    def close(self) -> bool:
        try:
            if self._conn is None:
                return True
            self._conn.close()
            return True
        except Exception:
            logging.exception("Error closing Postgres connection!")
            return False