from sqlalchemy import Column, Integer, String, Table, UniqueConstraint

from short_url.datasource import metadata

long_url_table = Table(
    "long_url",
    metadata,
    Column("pk", Integer, primary_key=True, autoincrement=True),
    Column("url", String, nullable=False),
    UniqueConstraint("url", name="url_uckey"),
)
