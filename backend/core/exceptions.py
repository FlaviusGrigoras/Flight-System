from dataclasses import dataclass


@dataclass
class DomainError(Exception):
    message: str
    code: str = "DOMAIN_ERROR"
    status: int = 400

    def __str__(self) -> str:
        return self.message


class ForbiddenError(DomainError):
    code = "FORBIDDEN"
    status = 403


class NotFoundError(DomainError):
    code = "NOT_FOUND"
    status = 404


class ValidationDomainError(DomainError):
    code = "VALIDATION_ERROR"
    status = 400
