from contextlib import contextmanager
from usecases import FetchRawProductDetailsUseCase
from entities import RawProductDetails
import psycopg
from typing import Optional, Sequence, overload, TypeVar, Iterator
from typing_extensions import override
import logging

T = TypeVar("T")


class PostgresFetchRawProductDetailsClient(FetchRawProductDetailsUseCase):
    def __init__(
        self,
        connection_string: str,
        raw_product_table_name: str,
        fetch_batch_size: int,
    ) -> None:
        super().__init__()
        self._connection_string = connection_string
        self._raw_product_table_name = raw_product_table_name
        self._fetch_batch_size = fetch_batch_size
        self._conn: Optional[psycopg.Connection] = None

    @overload
    def fetch(self, product_id: str) -> Optional[RawProductDetails]:
        ...

    @overload
    def fetch(self, product_id: Sequence[str]) -> list[Optional[RawProductDetails]]:
        ...

    @override
    def fetch(
        self, product_id: str | Sequence[str]
    ) -> Optional[RawProductDetails] | list[Optional[RawProductDetails]]:
        if isinstance(product_id, Sequence):
            return self._fetch_batch(product_id)
        return self._fetch_single(product_id)

    def _sql_tuple_to_raw_product_details(self, sql_tuple: tuple) -> RawProductDetails:
        """Deserialize SQL tuple to RawProductDetails"""
        return RawProductDetails(
            product_id=sql_tuple[0],
            name=sql_tuple[1],
            modified_date=sql_tuple[2],
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

    def _fetch_single(self, product_id: str) -> Optional[RawProductDetails]:
        """Fetch a single product details from the database"""
        try:
            with self._get_conn() as conn, conn.cursor() as cursor:
                stmt = """
                    SELECT
                        product_id,
                        name,
                        modified_date
                    FROM {table_name}
                        WHERE product_id = %s""".format(
                    table_name=self._raw_product_table_name
                )
                cursor.execute(stmt, (product_id,))
                result = cursor.fetchone()
                if result is None:
                    return None
                return self._sql_tuple_to_raw_product_details(result)
        except Exception:
            logging.exception("Error fetching product details from Postgres!")
            return None

    def _fetch_batch(
        self, product_id: Sequence[str]
    ) -> list[Optional[RawProductDetails]]:
        """Fetch a batch of product details from the database"""

        raw_product_details: list[Optional[RawProductDetails]] = []
        for product_ids_batch in self._batch_generator(
            product_id, self._fetch_batch_size
        ):
            try:
                with self._get_conn() as conn, conn.cursor() as cursor:
                    stmt = """
                        SELECT
                            product_id,
                            name,
                            modified_date
                        FROM {table_name}
                            WHERE product_id = ANY(%s)""".format(
                        table_name=self._raw_product_table_name
                    )
                    cursor.execute(stmt, (product_ids_batch,))
                    result = cursor.fetchall()
                    raw_product_details.extend(
                        [
                            self._sql_tuple_to_raw_product_details(row)
                            if row is not None
                            else None
                            for row in result
                        ]
                    )
            except Exception:
                logging.exception("Error fetching product details from Postgres!")
                raw_product_details.extend([None] * len(product_ids_batch))
        return raw_product_details

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
