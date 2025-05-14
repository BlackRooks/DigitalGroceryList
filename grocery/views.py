# FOR SQL AGGREGATION REFERENCE:https://www.coginiti.co/tutorials/intermediate/sql-sum/
from datetime import datetime, timedelta
# https://www.geeksforgeeks.org/python-program-to-convert-singular-to-plural/
import inflect
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.urls import NoReverseMatch
from typeguard import TypeCheckError

# Create your views here.
from .forms import CreateUserForm, GroceryListItemsForm, PantryAddForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GroceryListItems, GroceryList, StockAvailability, GroceryItem, PantryManagement, Category
from .filters import itemFilter, productFilter
pluralise = inflect.engine()
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Username or Password is incorrect.")
    # form=
    context = {}
    return render(request, "accounts/login.html", context)


def registerPage(request):
    form = CreateUserForm()
    client_group = Group.objects.get(name='client')
    if request.method == "POST":
        form = CreateUserForm(request.POST)  # using the Django form does the hashing for you
        if form.is_valid() :
            user = form.save()
            client_group.user_set.add(user)
            messages.success(request, f"Account for {user} is created.")
            return redirect("login")
        else:
            messages.error(request, f"We have an issue creating account:{form.errors}")
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def logoutUser(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("landing_page")


def landing_page(request):
    return render(request, 'landing.html')

def item_creation(request, grocery_list, item_name, quantity, category=None):
    """Helper function to handle item creation/update logic"""
    if not item_name:
        messages.error(request, "Item name cannot be empty.")
        return False

    try:
        quantity = float(quantity or 1)
        if quantity <= 0:
            messages.error(request, "Invalid quantity")
            return False

        # Get or create category and item
        if category:
            category_obj, _ = Category.objects.get_or_create(name=category)
            item, created = GroceryItem.objects.get_or_create(
                name=item_name,
                defaults={'category': category_obj}
            )
        else:
            item, created = GroceryItem.objects.get_or_create(name=item_name)

        # Update or create list item
        list_item = GroceryListItems.objects.filter(list=grocery_list, item=item).first()
        if list_item:
            list_item.quantity += quantity
            list_item.save()
            messages.success(request, "Quantity Updated successfully!")
        else:
            GroceryListItems.objects.create(
                list=grocery_list,
                item=item,
                quantity=quantity
            )
            messages.success(request, "Item added successfully!")
        return True
    except Exception as e:
        messages.error(request, f"Error adding item: {str(e)}")
        return False
@login_required
def home(request): #This is the render to the current url example
    latest_list = GroceryList.objects.filter(user=request.user).order_by('-created_at').first()
    items = GroceryListItems.objects.filter(list=latest_list) if latest_list else []
    list_name = latest_list.name if latest_list else "No List Available"
    pantryItems = PantryManagement.objects.filter(user=request.user).order_by("-expiration_date")
    if latest_list and request.method == "POST":
            item_name = request.POST.get("item_name", "").capitalize()
            category = request.POST.get("category")
            quantity = request.POST.get("quantity")

            success = item_creation(request, latest_list, item_name, quantity, category)
            if success:
                return redirect(request.META.get('HTTP_REFERER', 'home'))
    context = {"currentUser": request.user, 'items': items, "list_name": list_name, "list": latest_list,
               "pantryItems": pantryItems}
    return render(request, 'grocery/dashboard.html', context)


def grocery(request):
    store_filter = request.GET.get('store')
    products_list = StockAvailability.objects.all()
    if store_filter:
        products_list = products_list.filter(store__company__name=store_filter)

    product_filter = productFilter(request.GET, queryset=products_list)
    filtered_products = product_filter.qs

    paginator = Paginator(filtered_products, 25)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {"products": products, "product_filter": product_filter}
    return render(request, 'grocery/product.html', context)


@login_required
def lists(request):
    lists = GroceryList.objects.filter(user=request.user).order_by('-created_at')
    context = {"lists": lists}
    return render(request, 'grocery/lists.html', context)


@login_required
def grocery_list(request, pk_test):
    try:
        list = GroceryList.objects.get(id=pk_test, user=request.user)
        items = list.grocerylistitems_set.all()
        # createItem(request, list)
        if list:
            if request.method == "POST":
                item_name = request.POST.get("item_name", "").capitalize()
                category = request.POST.get("category")
                quantity = request.POST.get("quantity")

                success = item_creation(request, list, item_name, quantity, category)
                if success:
                    return redirect(request.META.get('HTTP_REFERER', 'home'))
        listFilter = itemFilter(request.GET, queryset=items)
        items = listFilter.qs

        context = {"list": list, "items": items, "listFilter": listFilter}
        return render(request, 'grocery/list_details.html', context)
    except GroceryList.DoesNotExist:
        messages.error(request, "The requested grocery list does not exist.")
        return redirect("lists")
    except NoReverseMatch:
        messages.error(request, "Invalid URL or arguments for the grocery list.")
        return redirect("lists")


@login_required
def add_list(request):
    if request.method == "POST":
        list_name = request.POST.get("list_name")
        if not list_name:
            messages.error(request, "List name cannot be empty.")
            return redirect("lists")
        grocery_list = GroceryList.objects.create(name=list_name, user=request.user)
        messages.success(request, "List created successfully!")
        return redirect("grocery_list", pk_test=grocery_list.id)
    return render(request, 'grocery/dashboard.html')


@login_required
def delete_list(request, list_id):
    try:
        grocery_list = GroceryList.objects.get(id=list_id, user=request.user)
        if request.user == grocery_list.user:
            grocery_list.delete()
            messages.success(request, "List deleted successfully")
        else:
            messages.error(request, "Permission denied")
    except GroceryList.DoesNotExist:
        messages.error(request, "List not found")
    return redirect("lists")


@login_required
def delete_item(request, item_id):
    try:
        list_item = GroceryListItems.objects.get(id=item_id, list__user=request.user)
        if request.user == list_item.list.user:
            list_item.delete()
            messages.success(request, "Item deleted successfully")
        else:
            messages.error(request, "Permission denied")
    except GroceryListItems.DoesNotExist:
        messages.error(request, "Item not found")
    return redirect("grocery_list", pk_test=list_item.list.id)


@login_required
def updateItem(request, item_id):
    list_item = GroceryListItems.objects.get(id=item_id, list__user=request.user)
    form = GroceryListItemsForm(instance=list_item)
    if request.method == "POST":
        form = GroceryListItemsForm(request.POST, instance=list_item)
        if form.is_valid():
            form.save()
            return redirect("grocery_list", pk_test=list_item.list.id)
    context = {"form": form, "list_name": list_item.list.name, "item_name": list_item.item.name}
    return render(request, 'features/update_item_form.html', context)


@login_required()
def save_list_to_pantry(request, list_id):
    try:
        grocery_list = GroceryList.objects.get(id=list_id, user=request.user)
        items_added = 0
        for list_item in grocery_list.grocerylistitems_set.all():
            # Only use get_or_create once
            pantry_item, created = PantryManagement.objects.get_or_create(
                user=grocery_list.user,
                name=list_item.item,
                purchase_date=datetime.now().date(),
                defaults={
                    'quantity': list_item.quantity,
                    'expiration_date': datetime.now().date() + timedelta(days=7)
                }
            )
            if not created:
                # If item exists, just update the quantity
                pantry_item.quantity += list_item.quantity
                pantry_item.save()
            items_added += 1
        messages.success(request, f"Added {items_added} items to pantry!")
        return redirect('home')
    except GroceryList.DoesNotExist:
        messages.error(request, "Grocery list not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

# def add_item_to_pantry(request):
#     if request.method == "POST":
#         form = PantryAddForm()
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Added items to pantry!")
#             return redirect('home')
#     else:
#         form = PantryAddForm()
#     return render(request, 'grocery/pantry.html', {'form': form})
@login_required()
def delete_pantry_item(request,pantry_item_id):
    try:
        pantry_item = PantryManagement.objects.get(id=pantry_item_id, user=request.user)
        if request.user == pantry_item.user:
            pantry_item.delete()
            messages.success(request, "Item deleted successfully")
        elif request.user != pantry_item.user:
            messages.error(request, "User Issue")
        else:
            messages.error(request, "Permission denied")
    except GroceryListItems.DoesNotExist:
        messages.error(request, "Item not found")

    return redirect("pantry")
@login_required()
def pantry(request):
    try:
        if request.method == "POST":
            form = PantryAddForm(request.POST, user=request.user)
            if form.is_valid():
                if form.is_valid():
                    # Get form data
                    item_name = form.cleaned_data['name']
                    quantity = form.cleaned_data['quantity']
                    expiration_date = form.cleaned_data['expiration_date']

                    existing_item = PantryManagement.objects.filter(
                        user=request.user,
                        name=item_name,
                        expiration_date=expiration_date
                    ).first()

                    if existing_item: # Update quantity if item exists
                        existing_item.quantity += quantity
                        existing_item.save()
                    else:# Create new item
                        form.save()
                messages.success(request, "Added items to pantry!")
                return redirect('pantry')
        else:
            form = PantryAddForm(user=request.user)

        pantryItems = PantryManagement.objects.filter(user=request.user).order_by('-name__category')
        context = {
            "pantryItems": pantryItems,
            "form": form
        }
        return render(request, 'grocery/pantry.html', context)
    except PantryManagement.DoesNotExist:
        messages.error(request, "Pantry not found.")
        return redirect('home')
@login_required()
def update_pantry_item(request, pantry_item_id):
    try:
        pantry_item = PantryManagement.objects.get(id=pantry_item_id, user=request.user)

        if request.method == "POST":
            form = PantryAddForm(request.POST, instance=pantry_item, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Item updated successfully!")
                return redirect('pantry')
        else:
            form = PantryAddForm(instance=pantry_item, user=request.user)

        context = {
            "form": form,
            "item_name": pantry_item.name
        }
        return render(request, 'features/update_pantry_item.html', context)

    except PantryManagement.DoesNotExist:
        messages.error(request, "Item not found.")
        return redirect('pantry')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("pantry")

def map(request):
    context = {'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'grocery/map.html', context)