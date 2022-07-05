import logging
from json import JSONDecodeError

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.requests import Request

from short_url.api.models import ErrorModel
from short_url.domain.exceptions import AlreadyExistsError, NotFoundError, UrlException

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")


def json_domain_error_handler(error: UrlException, status_code: int, request: Request):
    error_message = ErrorModel(code=error.code, message=str(error)).dict()
    return templates.TemplateResponse("exception.html", {"request": request, "status_code": status_code, **error_message})


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(UrlException)
    def handle_iam_exception(request: Request, error: UrlException):
        mapper = [
            (NotFoundError, 404),
            (AlreadyExistsError, 409),
            (UrlException, 400),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_domain_error_handler(error, status_code, request)

    @app.exception_handler(JSONDecodeError)
    def handle_json_decode_exception(request: Request, error: JSONDecodeError):
        message = str(jsonable_encoder(error.msg))
        err_content = ErrorModel(code="json_decode_error", message=message).dict()
        return templates.TemplateResponse("exception.html", {"request": request, "status_code": 400, **err_content})

    @app.exception_handler(ValidationError)
    def handle_validation_error(request: Request, error: ValidationError):
        err_content = ErrorModel(code="bad_request", message=str(error)).dict()
        return templates.TemplateResponse("exception.html", {"request": request, "status_code": 400, **err_content})

    @app.exception_handler(Exception)
    def handle_all_errors(request: Request, error: Exception):
        logger.error(f"Internal error {error}")
        err_content = ErrorModel(code="internal_error", message=str(error)).dict()
        return templates.TemplateResponse("exception.html", {"request": request, "status_code": 500, **err_content})
