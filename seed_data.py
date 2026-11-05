"""
Seed script to populate initial categories, an admin user, a verified vendor,
and sample services so the application can be explored immediately.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localvendor.settings')
django.setup()

from datetime import time
from accounts.models import User, CustomerProfile, VendorProfile
from services.models import ServiceCategory, Service, VendorAvailability

print("Seeding initial data...")

# 1. Create Default Categories
categories_data = [
    ("Home Cleaning", "Deep cleaning, carpet washing, and general domestic sanitation."),
    ("Plumbing Services", "Leak repair, pipeline installation, and bathroom fixtures."),
    ("Electrical Repair", "Wiring, appliance troubleshooting, and circuit repair."),
    ("Carpentry & Furniture", "Custom woodwork, door installation, and furniture fixes."),
    ("AC & Appliance Repair", "Servicing air conditioners, refrigerators, and washing machines."),
]

created_cats = []
for name, desc in categories_data:
    cat, _ = ServiceCategory.objects.get_or_create(name=name, defaults={'description': desc, 'is_active': True})
    created_cats.append(cat)
print(f"Created/Verified {len(created_cats)} categories.")

# 2. Create Admin Superuser
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@localvendor.com',
        'first_name': 'Site',
        'last_name': 'Administrator',
        'user_type': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('Admin@123')
    admin_user.save()
    print("Created Admin user: username='admin', password='Admin@123'")
else:
    print("Admin user already exists.")

# 3. Create Sample Verified Vendor
vendor_user, v_created = User.objects.get_or_create(
    username='raj_plumbing',
    defaults={
        'email': 'raj@quickfixplumbing.com',
        'first_name': 'Raj',
        'last_name': 'Kumar',
        'user_type': 'vendor',
    }
)
if v_created:
    vendor_user.set_password('Vendor@123')
    vendor_user.save()

vendor_profile, vp_created = VendorProfile.objects.get_or_create(
    user=vendor_user,
    defaults={
        'phone': '9876543210',
        'business_name': 'QuickFix Plumbing & Sanitation',
        'business_description': 'Over 10 years of experience serving residential and commercial properties with 24/7 emergency response.',
        'business_address': 'Shop #12, Market Complex',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'verification_status': 'approved',
        'is_active_vendor': True,
    }
)
if vp_created:
    print("Created Verified Vendor: username='raj_plumbing', password='Vendor@123'")

    # Add sample services
    plumbing_cat = ServiceCategory.objects.get(name="Plumbing Services")
    Service.objects.create(
        vendor=vendor_profile,
        category=plumbing_cat,
        name='Emergency Pipe Leak Repair',
        description='Quick fix for leaking pipes, valves, and bathroom drains.',
        price=499.00,
        duration_minutes=60,
        is_available=True,
    )
    Service.objects.create(
        vendor=vendor_profile,
        category=plumbing_cat,
        name='Complete Tap & Mixer Replacement',
        description='Replacement of old taps with new fixtures.',
        price=350.00,
        duration_minutes=45,
        is_available=True,
    )

    # Set weekly availability (Mon - Sat, 9 AM to 6 PM)
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    for day in days:
        VendorAvailability.objects.create(
            vendor=vendor_profile,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_available=True,
        )
    print("Created sample services and availability for vendor.")

# 4. Create Sample Customer
cust_user, c_created = User.objects.get_or_create(
    username='sneha_customer',
    defaults={
        'email': 'sneha@example.com',
        'first_name': 'Sneha',
        'last_name': 'Sharma',
        'user_type': 'customer',
    }
)
if c_created:
    cust_user.set_password('Customer@123')
    cust_user.save()
    CustomerProfile.objects.create(
        user=cust_user,
        phone='9123456780',
        address='Flat 402, Sunshine Apartments',
        city='Mumbai',
        state='Maharashtra',
        pincode='400001',
    )
    print("Created Customer user: username='sneha_customer', password='Customer@123'")

print("Seeding complete!")

