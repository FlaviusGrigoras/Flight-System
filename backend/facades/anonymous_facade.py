from facades.base_facade import FacadeBase
from django.contrib.auth import authenticate
from core.exceptions import ValidationDomainError

from accounts.models import Customer
from accounts.models import AirlineCompany


class AnonymousFacade(FacadeBase):
    def login(self, username, password):
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationDomainError("Invalid username or password.")
        return user

    def add_customer(self, user_data, customer_data):
        # user_data -> dictionar cu username, password, email
        # customer_data -> dictionar cu first_name, last_name, address, phone_no, credit_card_no
        user = self.create_user(**user_data)

        customer = Customer(user=user, **customer_data)
        return self.customer_repo.add(customer)

    def add_airline(self, user_data, airline_data):
        user = self.create_user(**user_data)

        airline = AirlineCompany(user=user, **airline_data)
        return self.airline_repo.add(airline)
