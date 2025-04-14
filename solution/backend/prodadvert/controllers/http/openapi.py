from typing import Any

from litestar.openapi import ResponseSpec

from prodadvert.controllers.http.schemas import CommonErrorSchema


def success_spec(
        description: str,
        container: type[Any] | None = None
) -> ResponseSpec:
    return ResponseSpec(
        description=description,
        data_container=container
    )


def error_spec(description: str) -> ResponseSpec:
    return ResponseSpec(
        description=description,
        data_container=CommonErrorSchema,
        generate_examples=False
    )
