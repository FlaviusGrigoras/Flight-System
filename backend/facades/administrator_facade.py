from facades.base_facade import FacadeBase
from accounts.models import Administrator
from core.exceptions import ForbiddenError, NotFoundError
import logging

logger = logging.getLogger("accounts")


class AdministratorFacade(FacadeBase):
    def __init__(self, user):
        super().__init__()
        self.user = user

        if not self.user.is_superuser:
            raise ForbiddenError("Access restricted to administrators only")

    def get_all_customers(self):
        return self.customer_repo.get_all()

    def add_administrator(self, user_data, admin_data):
        user = self.create_user(**user_data)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        admin = Administrator(user=user, **admin_data)
        admin.save()
        logger.info(f"New administrator created: {admin.first_name} {admin.last_name}")
        return admin

    def remove_airline(self, airline_id):
        airline = self.airline_repo.get_by_id(airline_id)
        if not airline:
            raise NotFoundError("Airline not found.")

        user_id = airline.user.id
        self.airline_repo.remove(airline.id)
        self.user_repo.remove(user_id)
        logger.info(f"Airline with ID {airline_id} removed by admin.")

    def remove_customer(self, customer_id):
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer not found")

        user_id = customer.user.id
        self.customer_repo.remove(customer_id)
        self.user_repo.remove(user_id)
        logger.info(f"Customer with ID {customer_id} removed by admin")
