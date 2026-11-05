"""
User model for the Local Vendor Connecting App.
We extend Django's AbstractUser to add a user_type field.
"""

import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractUser


# Helper functions for secure file uploads with UUID filenames
def profile_picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"profile_pictures/{unique_name}"


def vendor_document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"vendor_documents/{unique_name}"


class User(AbstractUser):
    """
    Custom User model - extends Django's AbstractUser.
    Adds user_type to tell if user is customer, vendor, or admin.
    """
    CUSTOMER = 'customer'
    VENDOR = 'vendor'
    ADMIN = 'admin'

    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (VENDOR, 'Vendor'),
        (ADMIN, 'Admin'),
    ]

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=CUSTOMER,
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class CustomerProfile(models.Model):
    """Stores customer-specific personal information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, blank=True, null=True)
    is_active_customer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


class VendorProfile(models.Model):
    """Stores vendor business details and verification status."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    VERIFICATION_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(blank=True)
    business_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, blank=True, null=True)
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default=PENDING)
    rejection_reason = models.TextField(blank=True)
    is_active_vendor = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vendor: {self.business_name} ({self.get_verification_status_display()})"


class VendorDocument(models.Model):
    """Stores vendor verification documents - SENSITIVE, admin-only access."""
    AADHAAR = 'aadhaar'
    PAN = 'pan'
    BUSINESS_LICENSE = 'business_license'
    OTHER = 'other'

    DOCUMENT_TYPE_CHOICES = [
        (AADHAAR, 'Aadhaar Card'),
        (PAN, 'PAN Card'),
        (BUSINESS_LICENSE, 'Business License'),
        (OTHER, 'Other Document'),
    ]

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to=vendor_document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.business_name} - {self.get_document_type_display()}"
