"""URL patterns for accounts app - registration, login, logout."""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/vendor/', views.vendor_register, name='vendor_register'),
    path('admin-login/', views.admin_login, name='admin_login'),
]

