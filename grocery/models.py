# Reference:https://docs.djangoproject.com/en/5.2/ref/models/instances/#django.db.models.Model.save
# Reference: https://docs.djangoproject.com/en/5.2/ref/models/fields/#field-options
from datetime import datetime, timedelta
from random import randint

from django.db import models
from django import forms

# Create your models here.
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=200)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"
class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    def __str__(self):
        return f"{self.name} ({self.brand})"


class GroceryCompany(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class GroceryStore(models.Model):
    company = models.ForeignKey(GroceryCompany, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)


class StockAvailability(models.Model):
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.quantity = randint(1, 100)  # Set quantity to a random value between 1 and 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.store.company.name})"


class GroceryList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_quantity(self):
        return self.grocerylistitems_set.aggregate(total=models.Sum('quantity'))['total'] or 0

    def __str__(self):
        return self.name


class GroceryItem(models.Model):
    name = models.CharField(max_length=200,unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    # # *** Do not uncomment unless implementing this - However, it's better to avoid due to speed - unless find a way to cache or optimise
    # # Reference: https://docs.djangoproject.com/en/5.2/topics/performance/
    # # This is place lower incase - so that they know product exist - to access other information like brand
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    # # Not yet implemented - but when the product is added from product - the name of product will be assigned
    # def save(self, *args, **kwargs):
    #     if not self.name and hasattr(self, 'product'):
    #         self.name = self.product.name
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class GroceryListItems(models.Model):
    list = models.ForeignKey(GroceryList, on_delete=models.CASCADE)
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    notes = models.CharField(max_length=255, blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"


class PantryManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    purchase_date = models.DateField()
    expiration_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('In stock', 'In stock'),
        ('Low', 'Low'),
        ('Out of stock', 'Out of stock')
    ])
    def is_expired(self):
            return self.expiration_date < datetime.now().date()

    def is_expiring_soon(self):
        if self.expiration_date:
            days_until_expiry = (self.expiration_date - datetime.now().date()).days
            return 0 < days_until_expiry <= 7
        return False

    def save(self, *args, **kwargs):
        self.status = "In stock" if self.quantity >= 4 else "Low" if 1 <= self.quantity <= 3 else "Out of stock"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.status})"
