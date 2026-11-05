"""URL patterns for vendor app."""

from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('services/', views.my_services, name='my_services'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('availability/', views.manage_availability, name='availability'),
    path('availability/<int:availability_id>/delete/', views.delete_availability, name='delete_availability'),
    path('bookings/received/', views.received_bookings, name='received_bookings'),
    path('bookings/upcoming/', views.upcoming_bookings, name='upcoming_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/accept/', views.accept_booking, name='accept_booking'),
    path('bookings/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('bookings/<int:booking_id>/complete/', views.complete_booking, name='complete_booking'),
    path('profile/', views.vendor_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

