from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from grocery.models import GroceryList, Category, GroceryItem, GroceryListItems


# Create your tests here.
class AccountsTests(TestCase):

    def setUp(self):
        self.username = 'jesspark'
        self.password = 'cupcake&1'
        self.email = "jessicapark@gmail.com"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        Group.objects.create(name='client')

    def test_matching_password_register_view(self):
        """UT-003: Test user registration with matching passwords"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'Str0ngP@ssw0rd!',
            'password2': 'Str0ngP@ssw0rd!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_valid_login_view(self):
        """UT-001: user login with valid credentials"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        """UT-002: Test user login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
        self.assertContains(response, 'Username or Password is incorrect.')

    def test_unmatching_password_registration(self):
        """UT-004: Test user registration with unmatching passwords"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'Str0ngP@ssw0rd!',
            'password2': 'StrongPass'
        })
        self.assertEqual(response.status_code, 200)  # Stays on registration page
        self.assertContains(response, "We have an issue creating account:")

    def test_existing_user_registration(self):
        """UT-005: Test user registration with existing username"""
        response = self.client.post(reverse('register'), {
            'username': 'jesspark',
            'email': 'testuser@gmail.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        })
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertContains(response, 'We have an issue creating account:')

    def test_logout_view(self):
        """UT-006: Test user logout"""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_invalid_email(self):
        """UT-007: Test registration with invalid email format"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'testuser',  # Invalid email format
            'password1': 'Str0ngP@ssw0rd!',
            'password2': 'Str0ngP@ssw0rd!'
        })
        self.assertEqual(response.status_code, 200) #stay on page
        self.assertContains(response, "Enter a valid email address")

    def test_missing_email(self):
        """UT-008: Test registration with missing email"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': '',  # Empty email
            'password1': 'Str0ngP@ssw0rd!',
            'password2': 'Str0ngP@ssw0rd!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(User.objects.filter(username='newuser').exists())


class ItemTests(TestCase):
    def setUp(self):
        self.username = 'jesspark'
        self.password = 'cupcake&1'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_valid_item_creation_home(self):
        """UT-0010: Create item with correct information"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        response = self.client.post(reverse('home'), {
            'list_id': grocery_list.id,
            'item_name': 'Apple',
            'quantity': 5,
            'category': 'Fruits'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Item added successfully!" in str(message) for message in messages))

    def test_empty_item_creation_grocery_list(self):
        """UT-009: Create item with all field empty"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        response = self.client.post(reverse('home'), {
            'list_id': grocery_list.id
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Item name cannot be empty." in str(message) for message in messages))

    def test_valid_item_creation_2_value(self):
        """UT-011: Create item with only name and quantity information"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        response = self.client.post(reverse('home'), {
            'list_id': grocery_list.id,
            'item_name': 'Banana ',
            'quantity': 3,
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Item added successfully!" in str(message) for message in messages))

    def test_invalid_quantity_item_creation(self):
        """UT-0014: Create item with invalid quantity"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        response = self.client.post(reverse('home'), {
            'item_name': 'Milk',
            'quantity': -1,
        })
        messages = list(get_messages(response.wsgi_request))
        for message in messages:
            print(f"Message: {message}")
            print(f"Message Level: {message.level}")
        self.assertTrue(any("Invalid quantity" in str(message) for message in messages))

    def test_create_with_only_name(self):
        """UT-012: Create item with only name information"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        response = self.client.post(reverse('home'), {
            'item_name': 'Orange'
        })
        messages = list(get_messages(response.wsgi_request))
        for message in messages:
            print(f"Message: {message}")
            print(f"Message Level: {message.level}")
        self.assertTrue(any("Item added successfully!" in str(message) for message in messages))
    def test_duplicate_item_creation(self):
        """UT-0013: Create item with an item already in the list"""
        grocery_list = GroceryList.objects.create(user=self.user, name="Test List")
        category = Category.objects.create(name="Fruits")
        item = GroceryItem.objects.create(name="Apple", category=category)
        GroceryListItems.objects.create(list=grocery_list, item=item, quantity=5)

        # Second creation of same item
        response = self.client.post(reverse('home'), {
            'item_name': 'Apple',
            'quantity': 2
        })
        messages = list(get_messages(response.wsgi_request))
        for message in messages:
            print(f"Message: {message}")
            print(f"Message Level: {message.level}")
        self.assertTrue(any("Quantity Updated successfully!" in str(message) for message in messages))