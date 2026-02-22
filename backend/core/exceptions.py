class DomainError(Exception):
    code = "DOMAIN_ERROR"
    status = 400

    def __init__(self, message: str, code: str = None, status: int = None):
        self.message = message
        self.code = code or self.__class__.code
        self.status = status if status is not None else self.__class__.status
        super().__init__(message)

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
