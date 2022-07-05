from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from short_url.datasource import metadata

short_url_table = Table(
    "short_url",
    metadata,
    Column("pk", Integer, primary_key=True, autoincrement=True),
    Column(
        "long_url_pk",
        Integer,
        ForeignKey("long_url.pk", ondelete="cascade", name="long_url_pk_fkey"),
        nullable=False,
    ),
    Column("url", String, nullable=False),
    UniqueConstraint("long_url_pk", "url", name="long_url_pk_short_url_uckey"),
)
