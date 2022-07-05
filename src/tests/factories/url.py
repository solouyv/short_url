from factory import Factory, Faker

from short_url.domain.entities import Url


class UrlFactory(Factory):
    class Meta:
        model = Url

    long_url = Faker("url")
    short_url = Faker("word")
