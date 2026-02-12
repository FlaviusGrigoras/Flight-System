from core.repository import BaseRepository
from geo.models import Country


class CountryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Country)
