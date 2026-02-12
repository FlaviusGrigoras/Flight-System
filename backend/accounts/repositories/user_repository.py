from core.repository import BaseRepository
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        return self.model.objects.filter(username=username).first()
