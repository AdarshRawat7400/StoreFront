from django.core.management.base import BaseCommand
from django.apps import apps
from django.forms.models import model_to_dict

class Command(BaseCommand):
    help = 'Import pages and slides to productionDB'

    def handle(self, *args, **options):
        Page = apps.get_model('store', 'Pages')
        Slide = apps.get_model('store', 'Slide')

        # Fetch all pages from the default database
        Page.objects.using('productionDB').all().delete()
        pages = Page.objects.using('default').all()

        for page in pages:
            # Create the page in productionDB
            page_in_production = Page.objects.using('productionDB').create(**model_to_dict(page, exclude=['id']))

            self.stdout.write(self.style.SUCCESS(f'Successfully imported page "{page.name}" to productionDB'))

        # Fetch all slides from the default database
        Slide.objects.using('productionDB').all().delete()
        slides = Slide.objects.using('default').all()

        for slide in slides:
            # Create the slide in productionDB
            slide_in_production = Slide.objects.using('productionDB').create(**model_to_dict(slide, exclude=['id']))

            self.stdout.write(self.style.SUCCESS(f'Successfully imported slide  to productionDB'))