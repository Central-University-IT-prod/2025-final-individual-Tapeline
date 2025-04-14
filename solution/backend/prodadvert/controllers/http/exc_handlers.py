from typing import Callable, Any, MutableMapping

from litestar import Request, Response
from litestar.exceptions import ValidationException

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException, InvalidDataException, \
    ForbiddenException


def handle_not_found(
        request: Request, exc: NotFoundException
) -> Response:
    return Response(
        content={
            "code": "NOT_FOUND",
            "detail": "Requested resource not found",
            "extra": exc.extra
        },
        status_code=404
    )


def handle_already_exists(
        request: Request, exc: AlreadyExistsException
) -> Response:
    return Response(
        content={
            "code": "ALREADY_EXISTS",
            "detail": (
                "Resource requested for creation "
                "conflicts with existing resource"
            ),
            "extra": exc.extra
        },
        status_code=409
    )


def handle_validation_exc(
        request: Request, exc: ValidationException
) -> Response:
    return Response(
        content={
            "code": "BAD_REQUEST",
            "detail": exc.detail,
            "extra": exc.extra
        },
        status_code=exc.status_code
    )


def handle_invalid_data(
        request: Request, exc: InvalidDataException
) -> Response:
    return Response(
        content={
            "code": "BAD_REQUEST",
            "detail": " ".join(map(str, exc.args)),
            "extra": exc.extra
        },
        status_code=400
    )


def handle_forbidden(
        request: Request, exc: ForbiddenException
) -> Response:
    return Response(
        content={
            "code": "FORBIDDEN",
            "detail": "Requested action is forbidden",
            "extra": exc.extra
        },
        status_code=403
    )


handler_mapping: MutableMapping[
    type[Exception], Callable[[Request[Any, Any, Any], Any], Response[Any]]
] = {
    NotFoundException: handle_not_found,
    AlreadyExistsException: handle_already_exists,
    ValidationException: handle_validation_exc,
    InvalidDataException: handle_invalid_data,
    ForbiddenException: handle_forbidden
}
