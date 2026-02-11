from core.repository import BaseRepository
from accounts.models import Customer


class CustomerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Customer)

    def get_customer_by_username(self, username):
        return self.model.objects.filter(user__username=username).first()
