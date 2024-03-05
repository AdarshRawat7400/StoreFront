import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from apps.store.models import Product, Review

class Command(BaseCommand):
    help = 'Generate dummy reviews for testing'

    def handle(self, *args, **options):
        fake = Faker()

        # Create a user for each review
        users = [get_user_model().objects.create(username=fake.user_name()) for _ in range(10)]

        # Create some products for testing
        products = [p for p in Product.objects.all()]

        # Generate 100 dummy reviews
        for _ in range(100):
            user = random.choice(users)
            product = random.choice(products)
            rating = random.randint(1, 5)
            comment = fake.paragraph()

            Review.objects.create(user=user, product=product, rating=rating, comment=comment)

        self.stdout.write(self.style.SUCCESS('Successfully generated 100 dummy reviews.'))
