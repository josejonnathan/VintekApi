from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from api_operations.models import Product, Category, CustomUser
from api_operations.models import ProductCondition


class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **kwargs):
        user_bishi = CustomUser.objects.get(username='bishi')
        user_teo = CustomUser.objects.get(username='teo')
        user_rea = CustomUser.objects.get(username='rea')

        categories = ['Cameras', 'Gaming Consoles', 'Radios', 'Televisions',
                      'PC', 'Walkman', 'Gaming', 'Nintendo', 'Mobile', 'Tablet', 'Server']
        category_objects = [Category.objects.create(
            name=cat) for cat in categories]

        products = [
            # User Bishi's products
            Product(name='Sony Vaio', brand='Sony', model='Vaio', produced_year=1985, country_of_origin='Japan', description='A vintage laptop', keywords='laptop, vintage, sony',
                    category=category_objects[4], condition=ProductCondition.GOOD, price=1000.00, user=user_bishi, publishing_date=timezone.now(), quantity=2, image=None),
            Product(name='Philco Model 90', brand='Philco', model='Model 90', produced_year=1931, country_of_origin='USA', description='A vintage radio', keywords='radio, vintage, philco',
                    category=category_objects[2], condition=ProductCondition.GOOD, price=150.00, user=user_bishi, publishing_date=timezone.now(), quantity=6, image=None),
            Product(name='Canon AE-1', brand='Canon', model='AE-1', produced_year=1976, country_of_origin='Japan', description='A vintage SLR camera', keywords='camera, vintage, canon',
                    category=category_objects[0], condition=ProductCondition.GOOD, price=300.00, user=user_bishi, publishing_date=timezone.now(), quantity=10, image=None),
            Product(name='Nikon D3000', brand='Nikon', model='D3000', produced_year=1999, country_of_origin='Japan', description='A vintage DSLR camera', keywords='camera, vintage, nikon',
                    category=category_objects[0], condition=ProductCondition.GOOD, price=200.00, user=user_bishi, publishing_date=timezone.now(), quantity=18, image=None),
            Product(name='Canon EOS-1D', brand='Canon', model='EOS-1D', produced_year=1998, country_of_origin='Japan', description='A vintage SLR camera', keywords='camera, vintage, canon',
                    category=category_objects[0], condition=ProductCondition.GOOD, price=300.00, user=user_bishi, publishing_date=timezone.now(), quantity=22, image=None),
            Product(name='Acer Aspire', brand='Acer', model='Aspire', produced_year=1998, country_of_origin='Japan', description='A vintage laptop', keywords='laptop, vintage, acer',
                    category=category_objects[4], condition=ProductCondition.GOOD, price=1000.00, user=user_bishi, publishing_date=timezone.now(), quantity=30, image=None),
            Product(name='Philips CD-100', brand='Philips', model='CD-100', produced_year=1954, country_of_origin='USA', description='A vintage transistor radio', keywords='radio, vintage, philips',
                    category=category_objects[2], condition=ProductCondition.GOOD, price=100.00, user=user_bishi, publishing_date=timezone.now(), quantity=14, image=None),
            # User Teo's products
            Product(name='Nintendo Entertainment System', brand='Nintendo', model='NES', produced_year=1985, country_of_origin='Japan', description='A classic home video game console',
                    keywords='gaming, retro, nintendo', category=category_objects[1], condition=ProductCondition.GOOD, price=150.00, user=user_teo, publishing_date=timezone.now(), quantity=5, image=None),
            Product(name='RCA CT-100', brand='RCA', model='CT-100', produced_year=1954, country_of_origin='USA', description='One of the first color televisions', keywords='television, vintage, RCA',
                    category=category_objects[3], condition=ProductCondition.GOOD, price=500.00, user=user_teo, publishing_date=timezone.now(), quantity=1, image=None),
            Product(name='Sega Genesis', brand='Sega', model='Genesis', produced_year=1989, country_of_origin='Japan', description='A classic home video game console',
                    keywords='gaming, retro, sega', category=category_objects[1], condition=ProductCondition.GOOD, price=200.00, user=user_teo, publishing_date=timezone.now(), quantity=4, image=None),
            Product(name='Samsung LC-45', brand='Samsung', model='LC-45', produced_year=1955, country_of_origin='South Korea', description='A vintage color television',
                    keywords='television, vintage, samsung', category=category_objects[3], condition=ProductCondition.GOOD, price=250.00, user=user_teo, publishing_date=timezone.now(), quantity=8, image=None),
            Product(name='LG 32LH20', brand='LG', model='32LH20', produced_year=2000, country_of_origin='South Korea', description='A vintage color television', keywords='television, vintage, LG',
                    category=category_objects[3], condition=ProductCondition.GOOD, price=150.00, user=user_teo, publishing_date=timezone.now(), quantity=16, image=None),
            Product(name='Panasonic DMC-FZ18', brand='Panasonic', model='DMC-FZ18', produced_year=1998, country_of_origin='Japan', description='A vintage DSLR camera',
                    keywords='camera, vintage, panasonic', category=category_objects[1], condition=ProductCondition.GOOD, price=200.00, user=user_teo, publishing_date=timezone.now(), quantity=20, image=None),
            Product(name='Olympus E-3', brand='Olympus', model='E-3', produced_year=1998, country_of_origin='Japan', description='A vintage DSLR camera', keywords='camera, vintage, olympus',
                    category=category_objects[1], condition=ProductCondition.GOOD, price=200.00, user=user_teo, publishing_date=timezone.now(), quantity=24, image=None),
            Product(name='Sony Playstation 1', brand='Sony', model='Playstation 1', produced_year=1998, country_of_origin='Japan', description='A vintage gaming console',
                    keywords='gaming, vintage, sony', category=category_objects[6], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=36, image=None),
            Product(name='Sony Playstation 2', brand='Sony', model='Playstation 2', produced_year=1998, country_of_origin='Japan', description='A vintage gaming console',
                    keywords='gaming, vintage, sony', category=category_objects[6], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=38, image=None),
            Product(name='Nintendo Wii', brand='Nintendo', model='Wii', produced_year=1998, country_of_origin='Japan', description='A vintage gaming console', keywords='gaming, vintage, nintendo',
                    category=category_objects[7], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=40, image=None),
            Product(name='Nintendo Gamecube', brand='Nintendo', model='Gamecube', produced_year=1998, country_of_origin='Japan', description='A vintage gaming console',
                    keywords='gaming, vintage, nintendo', category=category_objects[7], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=42, image=None),
            Product(name='Nintendo 64', brand='Nintendo', model='64', produced_year=1998, country_of_origin='Japan', description='A vintage gaming console', keywords='gaming, vintage, nintendo',
                    category=category_objects[7], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=44, image=None),
            Product(name='HP 15-bs0010na', brand='HP', model='15-bs0010na', produced_year=1998, country_of_origin='Japan', description='A vintage laptop', keywords='laptop, vintage, hp',
                    category=category_objects[4], condition=ProductCondition.GOOD, price=1000.00, user=user_teo, publishing_date=timezone.now(), quantity=32, image=None),
            # User Rea's products
            Product(name='Polaroid SX-70', brand='Polaroid', model='SX-70', produced_year=1972, country_of_origin='USA', description='A vintage instant camera', keywords='camera, vintage, polaroid',
                    category=category_objects[0], condition=ProductCondition.GOOD, price=250.00, user=user_rea, publishing_date=timezone.now(), quantity=3, image=None),
            Product(name='Zenith Royal 500', brand='Zenith', model='Royal 500', produced_year=1955, country_of_origin='USA', description='A vintage transistor radio',
                    keywords='radio, vintage, zenith', category=category_objects[2], condition=ProductCondition.GOOD, price=75.00, user=user_rea, publishing_date=timezone.now(), quantity=7, image=None),
            Product(name='Sony Cyber-shot DSC-W120', brand='Sony', model='DSC-W120', produced_year=1995, country_of_origin='Japan', description='A vintage DSLR camera',
                    keywords='camera, vintage, sony', category=category_objects[0], condition=ProductCondition.GOOD, price=200.00, user=user_rea, publishing_date=timezone.now(), quantity=12, image=None),
            Product(name='Nikon D300', brand='Nikon', model='D300', produced_year=1998, country_of_origin='Japan', description='A vintage DSLR camera', keywords='camera, vintage, nikon',
                    category=category_objects[0], condition=ProductCondition.GOOD, price=200.00, user=user_rea, publishing_date=timezone.now(), quantity=26, image=None),
            Product(name='Sony Alpha DSLR-A100', brand='Sony', model='DSLR-A100', produced_year=1998, country_of_origin='Japan', description='A vintage DSLR camera',
                    keywords='camera, vintage, sony', category=category_objects[0], condition=ProductCondition.GOOD, price=200.00, user=user_rea, publishing_date=timezone.now(), quantity=28, image=None),
            Product(name='Sony WM-EX194', brand='Sony', model='WM-EX194', produced_year=1998, country_of_origin='Japan', description='A vintage walkman', keywords='walkman, vintage, sony',
                    category=category_objects[5], condition=ProductCondition.GOOD, price=100.00, user=user_rea, publishing_date=timezone.now(), quantity=34, image=None),
            Product(name='Nokia 3310', brand='Nokia', model='3310', produced_year=1998, country_of_origin='Japan', description='A vintage mobile phone', keywords='mobile, vintage, nokia',
                    category=category_objects[8], condition=ProductCondition.GOOD, price=1000.00, user=user_rea, publishing_date=timezone.now(), quantity=46, image=None),
            Product(name='Nokia 6610', brand='Nokia', model='6610', produced_year=1998, country_of_origin='Japan', description='A vintage mobile phone', keywords='mobile, vintage, nokia',
                    category=category_objects[8], condition=ProductCondition.GOOD, price=1000.00, user=user_rea, publishing_date=timezone.now(), quantity=48, image=None),
            Product(name='Nokia 8210', brand='Nokia', model='8210', produced_year=1998, country_of_origin='Japan', description='A vintage mobile phone', keywords='mobile, vintage, nokia',
                    category=category_objects[8], condition=ProductCondition.GOOD, price=1000.00, user=user_rea, publishing_date=timezone.now(), quantity=50, image=None),
            Product(name='Apple iPad 1', brand='Apple', model='iPad 1', produced_year=1998, country_of_origin='Japan', description='A vintage tablet', keywords='tablet, vintage, apple',
                    category=category_objects[9], condition=ProductCondition.GOOD, price=1000.00, user=user_rea, publishing_date=timezone.now(), quantity=52, image=None),
            Product(name='Apple iPad 2', brand='Apple', model='iPad 2', produced_year=1998, country_of_origin='Japan', description='A vintage tablet', keywords='tablet, vintage, apple',
                    category=category_objects[9], condition=ProductCondition.GOOD, price=1000.00, user=user_rea, publishing_date=timezone.now(), quantity=54, image=None),

        ]

        # Save the products to the database
        for product in products:
            product.save()

        self.stdout.write(self.style.SUCCESS(
            'Database populated successfully'))

        # python manage.py populate_db
