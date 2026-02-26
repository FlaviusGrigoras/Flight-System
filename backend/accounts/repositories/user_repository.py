from core.repository import BaseRepository
from django.contrib.auth import get_user_model
from django.db import connection, DatabaseError

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        try:
            if connection.vendor == "postgresql":
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM get_user_by_username(%s);", [username])
                    row = cursor.fetchone()
                if not row:
                    return None
                return self.model.objects.filter(id=row[0]).first()
        except DatabaseError:
            pass

        return self.model.objects.filter(username=username).first()

    def exists_by_username(self, username):
        return self.model.objects.filter(username=username).exists()
