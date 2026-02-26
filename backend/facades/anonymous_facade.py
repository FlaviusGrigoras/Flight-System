from facades.base_facade import FacadeBase
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from core.exceptions import ValidationDomainError

from accounts.models import Customer
from accounts.models import AirlineCompany

import logging

logger = logging.getLogger("accounts")
User = get_user_model()


class AnonymousFacade(FacadeBase):
    def login(self, email, password):
        email = (email or "").strip().lower()
        usernames = list(
            User.objects.filter(email__iexact=email).values_list("username", flat=True)[
                :2
            ]
        )
        if len(usernames) != 1:
            raise ValidationDomainError("Invalid email or password.")

        user = authenticate(username=usernames[0], password=password)
        if not user:
            raise ValidationDomainError("Invalid email or password.")
        return user

    def add_customer(self, user_data, customer_data):
        # user_data -> username, password, email
        # customer_data -> first_name, last_name, address, phone_no, credit_card_no
        with transaction.atomic():
            user = self.create_user(**user_data, user_role_name="Customer")
            customer = Customer(user=user, **customer_data)
            saved_customer = super().add_customer(customer)
        logger.info(
            f"New customer registered: '{customer.first_name} {customer.last_name}' (Username: {user.username})."
        )

        return saved_customer

    def add_airline(self, user_data, airline_data):
        with transaction.atomic():
            user = self.create_user(**user_data, user_role_name="Airline Company")
            airline = AirlineCompany(user=user, **airline_data)
            saved_airline = super().add_airline(airline)

        logger.info(
            f"New airline company registered: '{airline.name}' (Username: {user.username})."
        )

        return saved_airline
