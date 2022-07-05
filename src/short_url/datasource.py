import logging
import threading
from contextlib import contextmanager
from enum import Enum
from typing import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.engine.url import URL

metadata = MetaData()

logger = logging.getLogger("datasource")


class DBDialect(Enum):
    POSTGRES = "postgresql"
    MSSQL = "mssql"


class DBDriver(Enum):
    PSYCOPG2 = "psycopg2"
    PYTDS = "pytds"
    PYODBC = "pyodbc"


class Database:
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect = DBDialect.POSTGRES,
        driver: DBDriver = DBDriver.PSYCOPG2,
        metaflags: dict = None,
    ) -> None:
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._database = database
        self._drivename = f"{dialect.value}+{driver.value}"
        self._metaflags = metaflags if metaflags is not None else {}

        self.engine: Engine = None
        self.engine_url: URL = None

        self._registry = threading.local()

    def get_connection(self) -> Connection:
        if not self.engine:
            raise ValueError("Database isn't configured")

        try:
            connection = self._registry.connection
            if connection is None:
                raise AttributeError()
        except AttributeError:
            logger.debug("Start new database connection")
            connection = self.configure_connection(self.engine.connect())
            self._registry.connection = connection

        return connection

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        connection = self.get_connection()

        transaction = connection.begin()
        try:
            yield connection
            transaction.commit()
        except BaseException:  # noqa: WPS424
            transaction.rollback()
            raise

    def configure_connection(self, connection) -> Connection:
        return connection.execution_options(autocommit=False)

    def connect(self) -> None:
        logger.debug("Initialize database engine")
        self.engine_url = URL(
            drivername=self._drivename,
            username=self._username,
            password=self._password,
            host=self._host,
            port=self._port,
            database=self._database,
            query=self._metaflags,
        )
        self.engine = create_engine(self.engine_url, convert_unicode=True, pool_size=5)

    def close(self) -> None:
        logger.debug("Close database connection")
        try:
            if self._registry.connection:
                self._registry.connection.close()
                self._registry.connection = None
        except AttributeError:
            pass

    def healthcheck(self):
        with self.connection() as conn:
            conn.execute("select 1;")
