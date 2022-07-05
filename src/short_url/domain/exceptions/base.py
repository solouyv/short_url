class UrlException(Exception):
    code = "url_exception"


class NotFoundError(UrlException):
    code = "not_found_error"


class AlreadyExistsError(UrlException):
    code = "already_exists_error"
