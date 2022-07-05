from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import delete, func, join, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import RowProxy
from sqlalchemy.engine.base import Connection
from sqlalchemy.exc import IntegrityError

from short_url.datasource import Database
from short_url.domain.entities import Url, Urls
from short_url.domain.exceptions import AlreadyExistsError, NotFoundError
from short_url.infrastructure.models import long_url_table, short_url_table


class UrlRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    def create(self, url: Url) -> Url:
        with self.db.connection() as conn:
            long_url_data = self._insert_long_url(conn, url.long_url)
            short_url = self._insert_short_url(conn, long_url_data, url.short_url)

        return Url(long_url=long_url_data["url"], short_url=short_url)

    def get(self, short_url: str) -> str:
        query = self._select_urls.where(short_url_table.c.url == short_url)
        with self.db.connection() as conn:
            res = conn.execute(query).fetchone()
        if not res:
            raise NotFoundError(f"Url '{short_url}' doesn't exist")

        return res.long_url

    def delete(self) -> None:
        with self.db.connection() as conn:
            conn.execute(delete(long_url_table))

    def get_list(self) -> list[Urls]:
        with self.db.connection() as conn:
            res = conn.execute(self._select_urls).fetchall()
        if not res:
            return res
        return [Urls(long_url=data.long_url, short_urls=data.short_urls) for data in res]

    @property
    def _select_urls(self):
        joined_tables = join(long_url_table, short_url_table, isouter=True)

        return (
            select(
                [
                    long_url_table.c.url.label("long_url"),
                    func.array_agg(short_url_table.c.url).label("short_urls"),
                ]
            )
            .select_from(joined_tables)
            .group_by(long_url_table.c.url)
        )

    @staticmethod
    def _insert_long_url(conn: Connection, url: str) -> RowProxy:
        query = (
            insert(long_url_table)
            .values(url=url)
            .on_conflict_do_update(index_elements=["url"], set_={"url": url})
            .returning(long_url_table)
        )

        return conn.execute(query).fetchone()

    @staticmethod
    def _insert_short_url(conn: Connection, long_url_data: RowProxy, url: str) -> str:
        query = insert(short_url_table).values(long_url_pk=long_url_data["pk"], url=url).returning(short_url_table)
        try:
            res = conn.execute(query).fetchone()
        except IntegrityError as err:
            if err.orig.pgcode == UNIQUE_VIOLATION:
                raise AlreadyExistsError(f"Short url '{url}' for url '{long_url_data.url}' already exists")
            raise

        return res["url"]
