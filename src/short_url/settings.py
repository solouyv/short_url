from pydantic import BaseSettings

from short_url.datasource import DBDialect, DBDriver


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: str
    db: str
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.PSYCOPG2

    class Config:
        env_prefix = "DATABASE_"


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    database: DatabaseSettings = DatabaseSettings()
