from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path("", views.landing_page, name="landing_page"),
    path("home/", views.home, name="home"),
    path("grocery/", views.grocery, name="grocery"),
    path("list/", views.lists, name="lists"),
    path('save_list_to_pantry/<int:list_id>/', views.save_list_to_pantry, name='save_list_to_pantry'),
    path("grocery_list/<str:pk_test>/", views.grocery_list, name="grocery_list"),
    path("delete_list/<int:list_id>/", views.delete_list, name='delete_list'),
    path("add_list/", views.add_list, name='add_list'),
    path("delete_item/<int:item_id>/", views.delete_item, name='delete_item'),
    path("logout/", views.logoutUser, name="logout"),
    path("update_item/<int:item_id>/", views.updateItem, name="update_item"),
    path("update_pantry_item/<int:pantry_item_id>/", views.update_pantry_item, name="update_pantry_item"),
    path("pantry/", views.pantry, name="pantry"),
    path("map/",views.map,name="map"),
    path("delete_pantry_item/<int:pantry_item_id>/",views.delete_pantry_item, name="delete_pantry_item")
]
