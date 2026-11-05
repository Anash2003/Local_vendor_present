"""URL patterns for customer app."""

from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('dashboard/', views.customer_dashboard, name='dashboard'),
    path('vendors/', views.browse_vendors, name='browse_vendors'),
    path('vendors/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('services/', views.browse_services, name='browse_services'),
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('profile/', views.customer_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

