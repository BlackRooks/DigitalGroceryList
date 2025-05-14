# Reference: https://testdriven.io/blog/django-performance-testing/
from datetime import datetime
from random import random, sample, choice, uniform, randint

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from faker import Faker

from grocery.models import GroceryItem, GroceryList, PantryManagement


class Command(BaseCommand):
    help = "Seeds the database with sample grocery items and grocery lists"

    def handle(self, unit_mappings=None, *args, **options):
        fake = Faker()

        # remove existing data
        GroceryItem.objects.all().delete()
        GroceryList.objects.all().delete()
        PantryManagement.objects.all().delete()

        # add 20 grocery items
        grocery_names = ["Apple", "Banana", "Carrot", "Tomato", "Potato", "Milk", "Bread", "Cheese", "Eggs", "Chicken", "Rice", "Pasta", "Beans", "Cereal", "Juice", "Butter", "Yogurt", "Fish", "Salt", "Sugar"]
        categories = ["Fruits", "Vegetables", "Dairy", "Bakery", "Meat", "Beverages"]
        items = [GroceryItem(name=name,category=choice(categories)) for name in sample(grocery_names, len(grocery_names))]
        GroceryItem.objects.bulk_create(items)
        default_user = User.objects.get_or_create(username='yoyopiya')[0]
        print(f"Grocery items created.")

        # add 5 grocery lists
        lists = []
        for _ in range(5):
            grocery_list = GroceryList(name=fake.sentence(nb_words=3), user=default_user)
            grocery_list.save()
            # add random items to the list
            for item in GroceryItem.objects.order_by('?')[:5]:
                grocery_list.grocerylistitems_set.create(item=item, quantity=fake.random_int(min=1, max=5))
            lists.append(grocery_list)
        print(f"Grocery lists created.")

        # add 10 pantry items
        for item in GroceryItem.objects.order_by('?')[:10]:
            PantryManagement.objects.create(user=default_user,unit="pieces" if item.category in ["Fruits", "Vegetables"] else "units", name=item,quantity=randint(0, 10),purchase_date=datetime.now().date(), expiration_date=fake.date_between(start_date="today", end_date="+30d"))
        print(f"Pantry items created.")