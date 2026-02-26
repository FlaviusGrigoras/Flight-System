from facades.base_facade import FacadeBase
from accounts.models import Administrator, AirlineCompany
from core.exceptions import ForbiddenError, NotFoundError, ValidationDomainError
from django.db import transaction
import logging

logger = logging.getLogger("accounts")


class AdministratorFacade(FacadeBase):
    def __init__(self, user):
        super().__init__()
        self.user = user

        if not self.user or not self.user.is_superuser:
            raise ForbiddenError("Access restricted to administrators only")

    def get_all_customers(self):
        return self.customer_repo.get_all_with_users()

    def get_all_airlines(self):
        return self.airline_repo.get_all_with_details()

    def get_all_administrators(self):
        return self.admin_repo.get_all_with_users()

    def add_airline(self, user_data, airline_data):
        with transaction.atomic():
            user = self.create_user(**user_data, user_role_name="Airline Company")
            airline = super().add_airline(AirlineCompany(user=user, **airline_data))
        logger.info(f"New airline created by admin: {airline.name}")
        return airline

    def add_administrator(self, user_data, admin_data):
        with transaction.atomic():
            user = self.create_user(**user_data, user_role_name="Administrator")
            user.is_superuser = True
            user.is_staff = True
            user.save(update_fields=["is_superuser", "is_staff"])

            admin = Administrator(user=user, **admin_data)
            admin.save()
        logger.info(f"New administrator created: {admin.first_name} {admin.last_name}")
        return admin

    def remove_airline(self, airline_id):
        airline = self.airline_repo.get_by_id(airline_id)
        if not airline:
            raise NotFoundError("Airline not found.")

        with transaction.atomic():
            self.user_repo.remove(airline.user_id)
        logger.info(f"Airline with ID {airline_id} removed by admin.")

        return True

    def remove_customer(self, customer_id):
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer not found")

        with transaction.atomic():
            self.user_repo.remove(customer.user_id)
        logger.info(f"Customer with ID {customer_id} removed by admin")

        return True

    def remove_administrator(self, administrator_id):
        administrator = self.admin_repo.get_by_id(administrator_id)
        if not administrator:
            raise NotFoundError("Administrator not found")

        if administrator.user_id == self.user.id:
            raise ValidationDomainError("You cannot remove your own administrator account")

        with transaction.atomic():
            self.user_repo.remove(administrator.user_id)
        logger.info(f"Administrator with ID {administrator_id} removed by admin")

        return True
