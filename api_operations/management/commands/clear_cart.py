# clear_cart.py

from django.core.management.base import BaseCommand
from api_operations.models import ShoppingCart

class Command(BaseCommand):
    help = 'Clears all data from the shopping cart'

    def handle(self, *args, **kwargs):
        try:
            ShoppingCart.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Shopping cart data cleared successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing shopping cart data: {e}'))
