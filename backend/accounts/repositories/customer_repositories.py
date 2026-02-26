from core.repository import BaseRepository
from accounts.models import Customer
from django.db import connection, DatabaseError


class CustomerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Customer)

    def get_customer_by_username(self, username):
        try:
            if connection.vendor == "postgresql":
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM get_customer_by_username(%s);", [username]
                    )
                    row = cursor.fetchone()
                if not row:
                    return None
                return self.model.objects.filter(id=row[0]).first()
        except DatabaseError:
            pass

        return self.model.objects.filter(user__username=username).first()

    def get_all_with_users(self):
        return self.model.objects.select_related("user").all()
