from rest_framework.views import exception_handler
from rest_framework.response import Response

from core.exceptions import DomainError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        return Response(
            {
                "error": {
                    "code": "DRF_ERROR",
                    "message": "Request failed validation.",
                    "details": detail,
                }
            },
            status=response.status_code,
        )

    if isinstance(exc, DomainError):
        return Response(
            {"error": {"code": exc.code, "message": exc.message}},
            status=exc.status,
        )

    return Response(
        {"error": {"code": "INTERNAL_ERROR", "message": "Unexpected error occurred."}},
        status=500,
    )
