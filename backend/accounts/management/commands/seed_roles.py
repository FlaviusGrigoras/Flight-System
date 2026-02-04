from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLE_AIRLINE_ADMIN = "AIRLINE_ADMIN"
ROLE_CUSTOMER = "CUSTOMER"


class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *args, **options):
        Group.objects.get_or_create(name=ROLE_AIRLINE_ADMIN)
        Group.objects.get_or_create(name=ROLE_CUSTOMER)
        self.stdout.write(self.style.SUCCESS("Seeded groups: AIRLINE_ADMIN, CUSTOMER"))
