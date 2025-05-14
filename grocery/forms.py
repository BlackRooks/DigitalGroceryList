from crispy_forms.layout import Layout, Field, Submit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import *
from crispy_forms.helper import FormHelper

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class GroceryListForm(forms.ModelForm):
    class Meta:
        model = GroceryList
        fields = ['name']


class GroceryItemForm(forms.ModelForm):
    class Meta:
        model = GroceryItem
        fields = ['name', 'category']


class GroceryListItemsForm(forms.ModelForm):
    class Meta:
        model = GroceryListItems
        fields = ['list', 'item', 'quantity', 'notes', 'completed']

    widgets = {
        'notes': forms.Textarea(attrs={'rows': 3}),
        'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'})
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['list'].disabled = True
        self.fields['item'].disabled = True
        # This section is important - for the crispy to work
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('list', placeholder='Enter the list name'),
            Field('item', placeholder='Enter the item name'),
            Field('quantity', placeholder='Enter the quantity'),
            Field('notes', placeholder='Enter notes'),
            Field('completed', type='checkbox'),
        )

class PantryAddForm(forms.ModelForm):
    name = forms.ModelChoiceField(
        queryset=GroceryItem.objects.all(),
        empty_label="Select an item"
    )
    quantity = forms.IntegerField()
    unit = forms.CharField()
    expiration_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "data-date-format": "dd/mm/yyyy"
            }
        )
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name="name",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("name"),
            Field("quantity"),
            Field("unit"),
            Field("expiration_date",placeholder="DD/MM/YYYY",type="date"),
            Field("category"),
            Submit("submit", "Add Item")
        )

    def save(self, commit=True):
        pantry_item = super().save(commit=False)
        pantry_item.user = self.user
        pantry_item.purchase_date = datetime.now()
        if commit:
            pantry_item.save()
        return pantry_item
    class Meta:
        model = PantryManagement
        fields = ["name", "quantity", "unit", "expiration_date","category"]