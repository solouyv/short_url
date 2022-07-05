from dataclasses import dataclass
from typing import Optional


@dataclass
class Url:
    long_url: str
    short_url: Optional[str]


@dataclass
class Urls:
    long_url: str
    short_urls: list[str]
