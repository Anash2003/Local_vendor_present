"""
Views for registration, login, logout.
Uses Django's built-in authenticate(), login(), logout() functions.
Session-based authentication only - NO JWT.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, CustomerProfile, VendorProfile, VendorDocument
from .forms import LoginForm, CustomerRegistrationForm, VendorRegistrationForm


def home(request):
    """Landing page of the website."""
    return render(request, 'home.html')


def customer_register(request):
    """Customer registration - creates User + CustomerProfile."""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('customer:dashboard')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Check if username already exists
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken. Please choose another.')
                return render(request, 'accounts/customer_register.html', {'form': form})

            # Check if email already exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'accounts/customer_register.html', {'form': form})

            # Create User (password is automatically hashed by create_user)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type='customer'
            )

            # Create CustomerProfile
            CustomerProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data.get('address', ''),
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                pincode=form.cleaned_data['pincode'],
            )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/customer_register.html', {'form': form})


def vendor_register(request):
    """Vendor registration - creates User + VendorProfile + VendorDocuments."""
    if request.user.is_authenticated:
        return redirect('vendor:dashboard')

    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken. Please choose another.')
                return render(request, 'accounts/vendor_register.html', {'form': form})

            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'accounts/vendor_register.html', {'form': form})

            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type='vendor'
            )

            # Create VendorProfile with pending status
            vendor_profile = VendorProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                business_name=form.cleaned_data['business_name'],
                business_description=form.cleaned_data.get('business_description', ''),
                business_address=form.cleaned_data['business_address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                pincode=form.cleaned_data['pincode'],
                verification_status='pending',
            )

            # Save uploaded documents
            aadhaar_file = form.cleaned_data.get('aadhaar_document')
            if aadhaar_file:
                VendorDocument.objects.create(
                    vendor=vendor_profile,
                    document_type='aadhaar',
                    document_file=aadhaar_file,
                )

            pan_file = form.cleaned_data.get('pan_document')
            if pan_file:
                VendorDocument.objects.create(
                    vendor=vendor_profile,
                    document_type='pan',
                    document_file=pan_file,
                )

            messages.success(
                request,
                'Registration successful! Your account is pending verification. '
                'Please wait for admin approval before logging in.'
            )
            return redirect('accounts:login')
    else:
        form = VendorRegistrationForm()

    return render(request, 'accounts/vendor_register.html', {'form': form})


def user_login(request):
    """
    Login view for customers and vendors.
    Uses Django authenticate() + login() → session created.
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.user_type == 'customer':
            return redirect('customer:dashboard')
        elif request.user.user_type == 'vendor':
            return redirect('vendor:dashboard')
        elif request.user.user_type == 'admin':
            return redirect('custom_admin:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Django authenticate() checks password hash - never plaintext
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Handle customer login
                if user.user_type == 'customer':
                    try:
                        profile = user.customer_profile
                        if not profile.is_active_customer:
                            messages.error(request, 'Your account has been deactivated. Please contact admin.')
                            return render(request, 'accounts/login.html', {'form': form})
                    except CustomerProfile.DoesNotExist:
                        messages.error(request, 'Customer profile not found. Please contact admin.')
                        return render(request, 'accounts/login.html', {'form': form})

                    # Django login() creates session
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('customer:dashboard')

                # Handle vendor login
                elif user.user_type == 'vendor':
                    try:
                        vendor = user.vendor_profile
                        if vendor.verification_status == 'pending':
                            messages.warning(
                                request,
                                'Your account is not verified yet. Your verification is currently '
                                'in process. Please wait for admin approval.'
                            )
                            return render(request, 'accounts/login.html', {'form': form})
                        elif vendor.verification_status == 'rejected':
                            reason = vendor.rejection_reason or 'Not specified'
                            messages.error(
                                request,
                                f'Your vendor registration has been rejected. Reason: {reason}'
                            )
                            return render(request, 'accounts/login.html', {'form': form})
                        elif not vendor.is_active_vendor:
                            messages.error(request, 'Your account has been deactivated. Please contact admin.')
                            return render(request, 'accounts/login.html', {'form': form})
                    except VendorProfile.DoesNotExist:
                        messages.error(request, 'Vendor profile not found. Please contact admin.')
                        return render(request, 'accounts/login.html', {'form': form})

                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('vendor:dashboard')

                # Admins should use admin login
                elif user.user_type == 'admin':
                    messages.info(request, 'Please use the admin login page.')
                    return redirect('accounts:admin_login')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def admin_login(request):
    """Separate login page for admin users."""
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect('custom_admin:dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None and user.user_type == 'admin' and user.is_staff:
                login(request, user)
                messages.success(request, 'Welcome to Admin Dashboard!')
                return redirect('custom_admin:dashboard')
            else:
                messages.error(request, 'Invalid admin credentials.')
    else:
        form = LoginForm()

    return render(request, 'accounts/admin_login.html', {'form': form})


def user_logout(request):
    """Logout - destroys Django session."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
