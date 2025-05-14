from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(GroceryItem)
admin.site.register(GroceryList)
admin.site.register(GroceryListItems)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(GroceryCompany)
admin.site.register(GroceryStore)
admin.site.register(StockAvailability)
admin.site.register(Category)
admin.site.register(PantryManagement)