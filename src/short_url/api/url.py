from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from short_url.api.models import UrlModel, UrlsModel
from short_url.containers import Services
from short_url.domain.services.url import UrlService

url_router = APIRouter(tags=["Url"])
templates = Jinja2Templates(directory="templates")


@url_router.post("/", response_model=UrlModel, status_code=HTTPStatus.CREATED)
@inject
def create_url(
    url_model: UrlModel,
    url_service: UrlService = Depends(Provide[Services.url]),
):
    return url_service.create(url_model.to_domain())


@url_router.get("/{short_url}", response_class=HTMLResponse)
@inject
def get_url(
    request: Request,
    short_url: str,
    url_service: UrlService = Depends(Provide[Services.url]),
):
    url = url_service.get(short_url)
    return RedirectResponse(url)


@url_router.delete("/", status_code=HTTPStatus.NO_CONTENT, response_class=HTMLResponse)
@inject
def delete_all(url_service: UrlService = Depends(Provide[Services.url])):
    return url_service.delete()


@url_router.get("/", response_model=list[UrlsModel], response_class=HTMLResponse)
@inject
def get_all(
    request: Request,
    url_service: UrlService = Depends(Provide[Services.url]),
):
    urls = url_service.get_list()
    return templates.TemplateResponse("urls.html", {"request": request, "urls": urls})
