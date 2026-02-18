import logging
from facades.base_facade import FacadeBase
from accounts.models import Administrator
from core.exceptions import ForbiddenError, NotFoundError

logger = logging.getLogger("accounts")


class AdministratorFacade(FacadeBase):
    def __init__(self, admin_user):
        super().__init__()
        if not admin_user.is_superuser:
            raise ForbiddenError("Access denied. Administrator privileges required.")
        self.admin_user = admin_user

    def add_administrator(self, user_data, admin_data):
        # user_data: dict (username, password, email)
        # admin_data:dict (first_name, last_name)

        user = self.create_user(**user_data)
        new_admin = Administrator.objects.create(user=user, **admin_data)
        logger.info(
            f"Admin {self.admin_user.username} created new admin: {user.username}"
        )
        return new_admin

    def remove_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        username = user.username
        user.delete()
        logger.info(f"Admin {self.admin_user.username} removed user: {username}")
        return True
