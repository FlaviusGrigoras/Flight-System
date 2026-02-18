from core.repository import BaseRepository
from accounts.models import Administrator


class AdministratorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Administrator)

    def get_admin_by_username(self, username):
        return self.model.objects.filter(user__username=username).first()

    def get_admin_by_user_id(self, user_id):
        return self.model.objects.select_related("user").filter(user_id=user_id).first()

    def update(self, admin_instance):
        admin_instance.save()
        return admin_instance

    def get_all_with_users(self):
        return self.model.objects.select_related("user").all()
