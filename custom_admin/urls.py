"""URL patterns for custom admin app."""

from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='dashboard'),

    # Customer management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:customer_id>/toggle/', views.toggle_customer_status, name='toggle_customer_status'),

    # Vendor management
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/pending/', views.pending_vendors, name='pending_vendors'),
    path('vendors/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<int:vendor_id>/edit/', views.vendor_edit, name='vendor_edit'),
    path('vendors/<int:vendor_id>/approve/', views.approve_vendor, name='approve_vendor'),
    path('vendors/<int:vendor_id>/reject/', views.reject_vendor, name='reject_vendor'),
    path('vendors/<int:vendor_id>/toggle/', views.toggle_vendor_status, name='toggle_vendor_status'),
    path('documents/<int:document_id>/', views.view_document, name='view_document'),

    # Booking management
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),

    # Service management
    path('services/', views.service_list, name='service_list'),
    path('categories/', views.service_categories, name='service_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/toggle/', views.toggle_category_status, name='toggle_category_status'),

    # Availability management
    path('availability/', views.availability_list, name='availability_list'),
]

