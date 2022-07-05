from shortuuid import uuid

from short_url.domain.entities import Url, Urls
from short_url.infrastructure.repositories import UrlRepository


class UrlService:
    def __init__(self, url_repository: UrlRepository):
        self._url_repository = url_repository

    def create(self, url: Url) -> Url:
        if not url.short_url:
            url.short_url = uuid(name=url.long_url.lower())
        self._normalize_urls(url)
        return self._url_repository.create(url)

    def get(self, short_url: str) -> str:
        return self._url_repository.get(short_url)

    def delete(self) -> None:
        return self._url_repository.delete()

    def get_list(self) -> list[Urls]:
        return self._url_repository.get_list()

    @staticmethod
    def _normalize_urls(url):
        url.long_url = url.long_url.lower()
        url.short_url = url.short_url.lower()
