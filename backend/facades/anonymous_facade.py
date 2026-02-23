from facades.base_facade import FacadeBase
from django.contrib.auth import authenticate
from django.db import transaction
from core.exceptions import ValidationDomainError

from accounts.models import Customer
from accounts.models import AirlineCompany

import logging

logger = logging.getLogger("accounts")


class AnonymousFacade(FacadeBase):
    def login(self, username, password):
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationDomainError("Invalid username or password.")
        return user

    def add_customer(self, user_data, customer_data):
        # user_data -> dictionar cu username, password, email
        # customer_data -> dictionar cu first_name, last_name, address, phone_no
        with transaction.atomic():
            user = self.create_user(**user_data)
            customer = Customer(user=user, **customer_data)
            saved_customer = self.customer_repo.add(customer)
        logger.info(
            f"New customer registered: '{customer.first_name} {customer.last_name}' (Username: {user.username})."
        )

        return saved_customer

    def add_airline(self, user_data, airline_data):
        with transaction.atomic():
            user = self.create_user(**user_data)
            airline = AirlineCompany(user=user, **airline_data)
            saved_airline = self.airline_repo.add(airline)

        logger.info(
            f"New airline company registered: '{airline.name}' (Username: {user.username})."
        )

        return saved_airline
