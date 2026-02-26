from core.repository import BaseRepository
from accounts.models import AirlineCompany
from django.db import connection, DatabaseError


class AirlineCompanyRepository(BaseRepository):
    def __init__(self):
        super().__init__(AirlineCompany)

    def get_airline_by_username(self, username):
        try:
            if connection.vendor == "postgresql":
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM get_airline_by_username(%s);", [username])
                    row = cursor.fetchone()
                if not row:
                    return None
                return self.model.objects.filter(id=row[0]).first()
        except DatabaseError:
            pass

        return self.model.objects.filter(user__username=username).first()

    def get_airlines_by_country(self, country_id):
        return self.model.objects.filter(country_id=country_id)

    def get_all_with_details(self):
        return self.model.objects.select_related("user", "country").all()
