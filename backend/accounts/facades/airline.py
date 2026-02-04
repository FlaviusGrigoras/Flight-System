from core.exceptions import ForbiddenError
from accounts.roles import ROLE_AIRLINE_ADMIN


class AirlineFacade:
    def __init__(self, user):
        self.user = user

    def _require_airline_admin(self):
        if not self.user.is_authenticated:
            raise ForbiddenError("Authentication required.")

        if (
            not self.user.groups.filter(name=ROLE_AIRLINE_ADMIN).exists()
            and not self.user.is_superuser
        ):
            raise ForbiddenError("Airline admin role required.")

    def _require_company(self):
        company = getattr(self.user, "airline_company", None)
        if company is None:
            raise ForbiddenError("User is not linked to any airline company.")
        return company
