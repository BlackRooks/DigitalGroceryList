from django.core.management.base import BaseCommand
from decimal import Decimal
import csv
from grocery.models import Product, Brand, Category, GroceryCompany, GroceryStore, StockAvailability
from django.db import transaction


class Command(BaseCommand):
    help = 'Import supermarket data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with transaction.atomic():
                with open(file_path, mode='r') as file:
                    reader = csv.DictReader(file, fieldnames=[
                        "supermarket", "prices_(£)", "prices_unit_(£)", "unit",
                        "names", "category", "own_brand", "brand"
                    ])

                    # Skip header row if exists
                    next(reader, None)

                    for row in reader:
                        # Create or get the brand
                        brand, _ = Brand.objects.get_or_create(name=row['brand'])

                        # Create or get the category
                        category_name = row['category'].replace('_', ' ').title()
                        category, _ = Category.objects.get_or_create(name=category_name)

                        # Create or get the product
                        product, _ = Product.objects.get_or_create(
                            name=row['names'],
                            defaults={
                                'brand': brand,
                                'category': category,
                                'description': row['names']
                            }
                        )

                        # Create or get the grocery company
                        company, _ = GroceryCompany.objects.get_or_create(name=row['supermarket'])

                        # Create or get the store
                        store, _ = GroceryStore.objects.get_or_create(
                            company=company,
                            defaults={
                                'address': 'Default Address',
                                'city': 'Default City',
                                'postcode': 'Default'
                            }
                        )

                        # Create or update stock availability
                        StockAvailability.objects.update_or_create(
                            store=store,
                            product=product,
                            defaults={
                                'price': Decimal(row['prices_(£)']),
                                'unit_price': Decimal(row['prices_unit_(£)']),
                                'quantity': 100
                            }
                        )
            self.stdout.write(self.style.SUCCESS('Successfully imported data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
            raise