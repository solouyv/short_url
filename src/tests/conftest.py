import pytest
from pytest_factoryboy import register
from starlette.testclient import TestClient

from short_url.fastapi_app import create_fastapi
from tests.factories.url import UrlFactory


@pytest.fixture(scope="session")
def app():
    fastapi_app = create_fastapi()

    yield fastapi_app


@pytest.fixture
def application(app):
    yield app.app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def config(application):
    yield application.config


@pytest.fixture
def repositories(application):
    yield application.repositories


@pytest.fixture
def url_repository(repositories):
    yield repositories.url


@pytest.fixture
def services(application):
    yield application.services


register(UrlFactory)
