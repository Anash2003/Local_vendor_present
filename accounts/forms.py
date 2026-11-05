"""
Forms for user registration and login.
Includes file upload validation for vendor documents.
"""

import os
from django import forms
from django.contrib.auth.password_validation import validate_password
from services.models import ServiceCategory


# Allowed file types and max size for document uploads
ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']
ALLOWED_CONTENT_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_document(file):
    """Validate uploaded document file - extension, content type, and size."""
    if file.size > MAX_FILE_SIZE:
        raise forms.ValidationError('File size must be less than 5 MB.')
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise forms.ValidationError('Allowed file types: PDF, JPG, JPEG, PNG.')
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise forms.ValidationError('Invalid file type uploaded.')


class LoginForm(forms.Form):
    """Simple login form with username and password."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    )


class CustomerRegistrationForm(forms.Form):
    """Registration form for customers."""
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'})
    )
    # Profile fields
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Address', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'})
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Pincode'})
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class VendorRegistrationForm(forms.Form):
    """Registration form for vendors with document uploads."""
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'})
    )
    # Business fields
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'})
    )
    business_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Business Name'})
    )
    business_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Describe your business', 'rows': 3})
    )
    business_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Business Address', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'})
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Pincode'})
    )
    # Document uploads
    aadhaar_document = forms.FileField(
        label='Aadhaar Card',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    pan_document = forms.FileField(
        label='PAN Card',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.jpg,.jpeg,.png'})
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def clean_aadhaar_document(self):
        file = self.cleaned_data.get('aadhaar_document')
        if file:
            validate_document(file)
        return file

    def clean_pan_document(self):
        file = self.cleaned_data.get('pan_document')
        if file:
            validate_document(file)
        return file

