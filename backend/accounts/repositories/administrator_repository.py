from core.repository import BaseRepository
from accounts.models import Administrator


class AdministratorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Administrator)
