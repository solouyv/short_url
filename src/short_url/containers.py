from dependency_injector import containers, providers, resources

from short_url.datasource import Database
from short_url.domain.services.url import UrlService
from short_url.infrastructure.repositories import UrlRepository


class DatabaseResource(resources.Resource):
    def init(self, username: str, password: str, host: str, port: int, database: str) -> Database:
        db = Database(username=username, password=password, host=host, port=port, database=database)
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.db,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()

    url: providers.Singleton[UrlRepository] = providers.Singleton(
        UrlRepository,
        database=datasources.postgres_datasource,
    )


class Services(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    url: providers.Factory[UrlService] = providers.Factory(
        UrlService,
        url_repository=repositories.url,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    core: providers.Container[Core] = providers.Container(Core, config=config)
    datasources: providers.Container[Datasources] = providers.Container(Datasources, config=config.database)
    repositories: providers.Container[Repositories] = providers.Container(Repositories, datasources=datasources)
    services: providers.Container[Services] = providers.Container(Services, repositories=repositories)
