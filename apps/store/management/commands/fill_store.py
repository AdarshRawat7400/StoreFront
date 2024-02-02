from django.core.management.base import BaseCommand
from django.apps import apps
from django.forms.models import model_to_dict

class Command(BaseCommand):
    help = 'Import categories, products, and tags to productionDB'

    def handle(self, *args, **options):
        Category = apps.get_model('store', 'Category')
        Product = apps.get_model('store', 'Product')
        Tag = apps.get_model('store', 'Tag')

        # Fetch all categories from the default database
        Category.objects.using('productionDB').all().delete()
        Category.objects.using('productionDB').all().delete()
        categories = Category.objects.using('default').all()

        for category in categories:
            # Create the category in productionDB
            category_in_production = Category.objects.using('productionDB').create(**model_to_dict(category, exclude=['id']))

            # Fetch products related to the current category
            products_to_copy = Product.objects.using('default').filter(category=category)

            # Copy each product to productionDB
            for product_to_copy in products_to_copy:
                product_data = model_to_dict(product_to_copy, exclude=['id', 'tags', 'category'])
                product_data['category'] = category_in_production
                product_in_production = Product.objects.using('productionDB').create(**product_data)

                # Copy tags related to the current product
                tags_to_copy = product_to_copy.tags.all()
                for tag_to_copy in tags_to_copy:
                    tag_data = model_to_dict(tag_to_copy, exclude=['id'])
                    product_in_production.tags.create(**tag_data)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported category "{category.name}", its products, and tags to productionDB'))
