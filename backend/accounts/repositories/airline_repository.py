from core.repository import BaseRepository
from accounts.models import AirlineCompany


class AirlineCompanyRepository(BaseRepository):
    def __init__(self):
        super().__init__(AirlineCompany)

    def get_airline_by_username(self, username):
        return self.model.objects.filter(user__username=username).first()

    def get_airlines_by_country(self, country_id):
        return self.model.objects.filter(country_id=country_id)

    def get_all_with_details(self):
        return self.model.objects.select_related("user", "country").all()
