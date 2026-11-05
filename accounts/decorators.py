"""
Custom authentication decorators for role-based access control.
These check user type and permissions in EVERY protected view.
"""

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def customer_required(view_func):
    """
    Decorator: allows access only to authenticated customers
    with active accounts.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        # Check if user is a customer
        if request.user.user_type != 'customer':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:login')
        # Check if customer profile exists and is active
        try:
            profile = request.user.customer_profile
            if not profile.is_active_customer:
                messages.error(request, 'Your account has been deactivated. Please contact admin.')
                from django.contrib.auth import logout
                logout(request)
                return redirect('accounts:login')
        except Exception:
            messages.error(request, 'Customer profile not found.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def vendor_required(view_func):
    """
    Decorator: allows access only to authenticated, APPROVED vendors
    with active accounts.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        # Check if user is a vendor
        if request.user.user_type != 'vendor':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:login')
        # Check vendor profile status
        try:
            vendor = request.user.vendor_profile
            if vendor.verification_status == 'pending':
                messages.warning(
                    request,
                    'Your account is not verified yet. Your verification is currently '
                    'in process. Please wait for admin approval.'
                )
                from django.contrib.auth import logout
                logout(request)
                return redirect('accounts:login')
            if vendor.verification_status == 'rejected':
                reason = vendor.rejection_reason or 'Not specified'
                messages.error(
                    request,
                    f'Your vendor registration has been rejected. Reason: {reason}'
                )
                from django.contrib.auth import logout
                logout(request)
                return redirect('accounts:login')
            if not vendor.is_active_vendor:
                messages.error(request, 'Your account has been deactivated. Please contact admin.')
                from django.contrib.auth import logout
                logout(request)
                return redirect('accounts:login')
        except Exception:
            messages.error(request, 'Vendor profile not found.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    Decorator: allows access only to authenticated admin users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:admin_login')
        # Check if user is admin
        if request.user.user_type != 'admin' or not request.user.is_staff:
            messages.error(request, 'You do not have admin permissions.')
            return redirect('accounts:admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

