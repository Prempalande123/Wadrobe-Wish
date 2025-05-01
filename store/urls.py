from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Storefront and Product Views
    path('', views.store, name="store"),
    path('product/<str:pk>/', views.viewProduct, name="product"),
    path('search/', views.search, name="search"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    # Authentication
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name="login"),  # renamed to avoid conflict with Django's login
    path('logout/', views.logout, name='logout'),  # redirects to home after logout

    # Cart / Order Actions
    path('updateItem/', views.updateItem, name="updateItem"),
    path('processOrder/', views.processOrder, name="processOrder"),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),

]
