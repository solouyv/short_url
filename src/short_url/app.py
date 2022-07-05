import logging

from short_url import api
from short_url.containers import Application
from short_url.settings import Settings

logger = logging.getLogger(__name__)


def init_application() -> Application:
    app = Application()
    app.config.from_pydantic(Settings())
    app.init_resources()
    app.services.wire(packages=(api,))

    return app
