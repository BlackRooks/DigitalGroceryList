import django_filters
from .models import *
# Reference: https://forum.djangoproject.com/t/using-django-filter-to-filter-data-from-two-related-models/39565/2
class itemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='item__name', lookup_expr='icontains', label='Item Name')
    class Meta:
        model=GroceryListItems
        fields = ["name","quantity","notes","completed"]
        exclude = ["list","item"]

class productFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains', label='Product Name')
    brand_name = django_filters.CharFilter(field_name='product__brand__name', lookup_expr='icontains', label="Brand")
    class Meta:
        model=StockAvailability
        fields = ["name","price"]
        exclude = ["store","product","quantity","last_updated","unit_price"]