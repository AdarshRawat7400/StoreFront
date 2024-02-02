
import random
from django.core.management.base import BaseCommand
from faker import Faker
from apps.users.models import Users  # Adjust the import statement based on your app structure

fake = Faker()

class Command(BaseCommand):
    help = 'Create fake Users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating fake Users...'))

        for _ in range(5000):
            while True:
                username = fake.user_name()
                if not Users.objects.filter(username=username).exists():
                    break

            Users.objects.create(
                username=username,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                dob=fake.date_of_birth(),
                full_name=fake.name(),
                state=fake.state(),
                complete_address=fake.address(),
                phone_number=fake.phone_number(),
                city=fake.city(),
                country=fake.country(),
                postal_code=fake.zipcode(),
                about_me=fake.text(),
                balance=random.uniform(0, 10000),
                system_id='C',  # Set to your desired logic
                role="customer",  # Always set to "customer"
            )

        self.stdout.write(self.style.SUCCESS('Successfully created fake Users!'))

