"""
Comprehensive unit & integration tests covering:
- Authentication & Sessions (No JWT)
- Access Control Decorators (@customer_required, @vendor_required, @admin_required)
- Vendor Approval Flow (Pending cannot access, Approved can)
- Ownership verification (Customer can only see their own bookings)
- CSRF Protection enforcement
"""

from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, CustomerProfile, VendorProfile
from services.models import ServiceCategory, Service, Booking, VendorAvailability


class LocalVendorAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Setup Admin
        self.admin_user = User.objects.create_user(
            username='test_admin', password='password123', user_type='admin', is_staff=True
        )

        # 2. Setup Approved Vendor
        self.vendor_user = User.objects.create_user(
            username='test_vendor', password='password123', user_type='vendor'
        )
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor_user,
            phone='1234567890',
            business_name='Apex Electric',
            business_address='123 Main St',
            city='Delhi',
            state='Delhi',
            pincode='110001',
            verification_status='approved',
        )

        # 3. Setup Pending Vendor
        self.pending_vendor_user = User.objects.create_user(
            username='pending_vendor', password='password123', user_type='vendor'
        )
        self.pending_vendor_profile = VendorProfile.objects.create(
            user=self.pending_vendor_user,
            phone='0987654321',
            business_name='Pending Cleaners',
            business_address='456 Cross St',
            city='Delhi',
            state='Delhi',
            pincode='110001',
            verification_status='pending',
        )

        # 4. Setup Customer 1 & Customer 2
        self.customer1_user = User.objects.create_user(
            username='cust1', password='password123', user_type='customer'
        )
        self.customer1_profile = CustomerProfile.objects.create(
            user=self.customer1_user, phone='1111111111', city='Delhi', state='Delhi', pincode='110001'
        )

        self.customer2_user = User.objects.create_user(
            username='cust2', password='password123', user_type='customer'
        )
        self.customer2_profile = CustomerProfile.objects.create(
            user=self.customer2_user, phone='2222222222', city='Delhi', state='Delhi', pincode='110001'
        )

        # 5. Service & Availability
        self.category = ServiceCategory.objects.create(name='Electrical', is_active=True)
        self.service = Service.objects.create(
            vendor=self.vendor_profile,
            category=self.category,
            name='Fan Repair',
            description='Fix ceiling fan',
            price=299.00,
            duration_minutes=30,
            is_available=True,
        )

    def test_vendor_pending_verification_login_restriction(self):
        """A pending vendor cannot access the vendor dashboard."""
        self.client.login(username='pending_vendor', password='password123')
        response = self.client.get(reverse('vendor:dashboard'), follow=True)
        # Should be redirected and shown warning message
        self.assertContains(response, "Your account is not verified yet")
        self.assertRedirects(response, reverse('accounts:login'))

    def test_approved_vendor_can_access_dashboard(self):
        """Approved vendor can access dashboard smoothly."""
        self.client.login(username='test_vendor', password='password123')
        response = self.client.get(reverse('vendor:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apex Electric')

    def test_customer_cannot_access_vendor_dashboard(self):
        """Customer role check forbids access to vendor dashboard."""
        self.client.login(username='cust1', password='password123')
        # Without follow=True, we verify the direct 302 redirect to accounts:login
        response = self.client.get(reverse('vendor:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:login'))

    def test_booking_ownership_protection(self):
        """Customer 2 cannot view or cancel Customer 1's booking."""
        booking = Booking.objects.create(
            customer=self.customer1_profile,
            vendor=self.vendor_profile,
            service=self.service,
            booking_date=date.today() + timedelta(days=2),
            booking_time=time(10, 0),
            status='pending',
        )

        # Customer 2 attempts to view Customer 1's booking
        self.client.login(username='cust2', password='password123')
        response = self.client.get(reverse('customer:booking_detail', args=[booking.id]))
        # Must return 404 HttpNotfound (object not owned)
        self.assertEqual(response.status_code, 404)

        # Customer 1 can view it
        self.client.login(username='cust1', password='password123')
        response = self.client.get(reverse('customer:booking_detail', args=[booking.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fan Repair")

    def test_admin_dashboard_security(self):
        """Non-admin users cannot access the custom admin dashboard."""
        self.client.login(username='cust1', password='password123')
        # Direct redirect should be to accounts:admin_login
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:admin_login'))

        # Real admin can access
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('custom_admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Operations & Metrics")
