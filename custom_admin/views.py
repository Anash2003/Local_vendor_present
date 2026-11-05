"""
Custom admin views - full platform management.
All views use @admin_required decorator.
"""

import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib import messages
from accounts.decorators import admin_required
from accounts.models import User, CustomerProfile, VendorProfile, VendorDocument
from services.models import Service, ServiceCategory, Booking, VendorAvailability
from .forms import (
    ServiceCategoryForm, VendorRejectionForm,
    AdminCustomerEditForm, AdminVendorEditForm
)


# ===================== DASHBOARD =====================

@admin_required
def admin_dashboard(request):
    """Admin dashboard with platform overview stats."""
    context = {
        'total_customers': CustomerProfile.objects.count(),
        'total_vendors': VendorProfile.objects.count(),
        'approved_vendors': VendorProfile.objects.filter(verification_status='approved').count(),
        'pending_vendors': VendorProfile.objects.filter(verification_status='pending').count(),
        'rejected_vendors': VendorProfile.objects.filter(verification_status='rejected').count(),
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'confirmed_bookings': Booking.objects.filter(status='confirmed').count(),
        'completed_bookings': Booking.objects.filter(status='completed').count(),
        'total_services': Service.objects.count(),
        'total_categories': ServiceCategory.objects.count(),
        'recent_customers': CustomerProfile.objects.order_by('-created_at')[:5],
        'recent_vendors': VendorProfile.objects.order_by('-created_at')[:5],
        'recent_bookings': Booking.objects.order_by('-created_at')[:5],
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ===================== CUSTOMER MANAGEMENT =====================

@admin_required
def customer_list(request):
    """View all registered customers."""
    customers = CustomerProfile.objects.all().order_by('-created_at')

    # Search filter
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(user__username__icontains=search)

    context = {
        'customers': customers,
        'search': search,
    }
    return render(request, 'custom_admin/customer_list.html', context)


@admin_required
def customer_detail(request, customer_id):
    """View individual customer details."""
    customer = get_object_or_404(CustomerProfile, id=customer_id)
    bookings = Booking.objects.filter(customer=customer).order_by('-created_at')[:10]

    context = {
        'customer': customer,
        'bookings': bookings,
    }
    return render(request, 'custom_admin/customer_detail.html', context)


@admin_required
def customer_edit(request, customer_id):
    """Edit customer details."""
    customer = get_object_or_404(CustomerProfile, id=customer_id)

    if request.method == 'POST':
        form = AdminCustomerEditForm(request.POST)
        if form.is_valid():
            # Update user fields
            customer.user.first_name = form.cleaned_data['first_name']
            customer.user.last_name = form.cleaned_data['last_name']
            customer.user.email = form.cleaned_data['email']
            customer.user.save()

            # Update profile fields
            customer.phone = form.cleaned_data.get('phone', '')
            customer.city = form.cleaned_data.get('city', '')
            customer.state = form.cleaned_data.get('state', '')
            customer.pincode = form.cleaned_data.get('pincode', '')
            customer.save()

            messages.success(request, 'Customer details updated.')
            return redirect('custom_admin:customer_detail', customer_id=customer.id)
    else:
        form = AdminCustomerEditForm(initial={
            'first_name': customer.user.first_name,
            'last_name': customer.user.last_name,
            'email': customer.user.email,
            'phone': customer.phone,
            'city': customer.city,
            'state': customer.state,
            'pincode': customer.pincode,
        })

    context = {
        'form': form,
        'customer': customer,
    }
    return render(request, 'custom_admin/customer_edit.html', context)


@admin_required
def toggle_customer_status(request, customer_id):
    """Activate or deactivate a customer account - POST only."""
    if request.method == 'POST':
        customer = get_object_or_404(CustomerProfile, id=customer_id)
        customer.is_active_customer = not customer.is_active_customer
        customer.save()
        status = 'activated' if customer.is_active_customer else 'deactivated'
        messages.success(request, f'Customer account {status}.')
    return redirect('custom_admin:customer_detail', customer_id=customer_id)


# ===================== VENDOR MANAGEMENT =====================

@admin_required
def vendor_list(request):
    """View all registered vendors."""
    vendors = VendorProfile.objects.all().order_by('-created_at')

    # Status filter
    status = request.GET.get('status', '')
    if status:
        vendors = vendors.filter(verification_status=status)

    # Search filter
    search = request.GET.get('search', '')
    if search:
        vendors = vendors.filter(business_name__icontains=search)

    context = {
        'vendors': vendors,
        'selected_status': status,
        'search': search,
    }
    return render(request, 'custom_admin/vendor_list.html', context)


@admin_required
def pending_vendors(request):
    """View pending vendor registrations for approval."""
    vendors = VendorProfile.objects.filter(verification_status='pending').order_by('-created_at')

    context = {
        'vendors': vendors,
    }
    return render(request, 'custom_admin/pending_vendors.html', context)


@admin_required
def vendor_detail(request, vendor_id):
    """View vendor details including uploaded documents."""
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    documents = VendorDocument.objects.filter(vendor=vendor)
    services = Service.objects.filter(vendor=vendor)
    bookings = Booking.objects.filter(vendor=vendor).order_by('-created_at')[:10]

    context = {
        'vendor': vendor,
        'documents': documents,
        'services': services,
        'bookings': bookings,
        'rejection_form': VendorRejectionForm(),
    }
    return render(request, 'custom_admin/vendor_detail.html', context)


@admin_required
def vendor_edit(request, vendor_id):
    """Edit vendor details."""
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    if request.method == 'POST':
        form = AdminVendorEditForm(request.POST)
        if form.is_valid():
            vendor.user.first_name = form.cleaned_data['first_name']
            vendor.user.last_name = form.cleaned_data['last_name']
            vendor.user.email = form.cleaned_data['email']
            vendor.user.save()

            vendor.phone = form.cleaned_data['phone']
            vendor.business_name = form.cleaned_data['business_name']
            vendor.business_description = form.cleaned_data.get('business_description', '')
            vendor.business_address = form.cleaned_data['business_address']
            vendor.city = form.cleaned_data['city']
            vendor.state = form.cleaned_data['state']
            vendor.pincode = form.cleaned_data['pincode']
            vendor.save()

            messages.success(request, 'Vendor details updated.')
            return redirect('custom_admin:vendor_detail', vendor_id=vendor.id)
    else:
        form = AdminVendorEditForm(initial={
            'first_name': vendor.user.first_name,
            'last_name': vendor.user.last_name,
            'email': vendor.user.email,
            'phone': vendor.phone,
            'business_name': vendor.business_name,
            'business_description': vendor.business_description,
            'business_address': vendor.business_address,
            'city': vendor.city,
            'state': vendor.state,
            'pincode': vendor.pincode,
        })

    context = {
        'form': form,
        'vendor': vendor,
    }
    return render(request, 'custom_admin/vendor_edit.html', context)


@admin_required
def approve_vendor(request, vendor_id):
    """Approve a pending vendor - POST only."""
    if request.method == 'POST':
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.verification_status = 'approved'
        vendor.rejection_reason = ''
        vendor.save()
        messages.success(request, f'Vendor "{vendor.business_name}" has been approved!')
    return redirect('custom_admin:vendor_detail', vendor_id=vendor_id)


@admin_required
def reject_vendor(request, vendor_id):
    """Reject a vendor with reason - POST only."""
    if request.method == 'POST':
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        form = VendorRejectionForm(request.POST)
        if form.is_valid():
            vendor.verification_status = 'rejected'
            vendor.rejection_reason = form.cleaned_data['rejection_reason']
            vendor.save()
            messages.success(request, f'Vendor "{vendor.business_name}" has been rejected.')
    return redirect('custom_admin:vendor_detail', vendor_id=vendor_id)


@admin_required
def toggle_vendor_status(request, vendor_id):
    """Activate or deactivate a vendor - POST only."""
    if request.method == 'POST':
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.is_active_vendor = not vendor.is_active_vendor
        vendor.save()
        status = 'activated' if vendor.is_active_vendor else 'deactivated'
        messages.success(request, f'Vendor account {status}.')
    return redirect('custom_admin:vendor_detail', vendor_id=vendor_id)


@admin_required
def view_document(request, document_id):
    """
    Serve vendor document file - ADMIN ONLY.
    Documents are not publicly accessible.
    """
    document = get_object_or_404(VendorDocument, id=document_id)
    try:
        file_path = document.document_file.path
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(
            open(file_path, 'rb'),
            content_type=content_type or 'application/octet-stream'
        )
    except FileNotFoundError:
        raise Http404('Document file not found.')


# ===================== BOOKING MANAGEMENT =====================

@admin_required
def booking_list(request):
    """View all bookings with filters."""
    bookings = Booking.objects.all().order_by('-created_at')

    # Status filter
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)

    # Search filter
    search = request.GET.get('search', '')
    if search:
        bookings = bookings.filter(
            customer__user__username__icontains=search
        ) | bookings.filter(
            vendor__business_name__icontains=search
        )

    context = {
        'bookings': bookings,
        'selected_status': status,
        'search': search,
    }
    return render(request, 'custom_admin/booking_list.html', context)


@admin_required
def booking_detail(request, booking_id):
    """View individual booking details."""
    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'booking': booking,
    }
    return render(request, 'custom_admin/booking_detail.html', context)


# ===================== SERVICE MANAGEMENT =====================

@admin_required
def service_list(request):
    """View all services."""
    services = Service.objects.all().order_by('-created_at')

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        services = services.filter(category_id=category_id)

    categories = ServiceCategory.objects.all()

    context = {
        'services': services,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'custom_admin/service_list.html', context)


@admin_required
def service_categories(request):
    """View and manage service categories."""
    categories = ServiceCategory.objects.all().order_by('name')

    context = {
        'categories': categories,
        'form': ServiceCategoryForm(),
    }
    return render(request, 'custom_admin/service_categories.html', context)


@admin_required
def add_category(request):
    """Add a new service category - POST only."""
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if ServiceCategory.objects.filter(name__iexact=name).exists():
                messages.error(request, 'Category with this name already exists.')
            else:
                ServiceCategory.objects.create(
                    name=name,
                    description=form.cleaned_data.get('description', ''),
                )
                messages.success(request, 'Category added successfully!')
    return redirect('custom_admin:service_categories')


@admin_required
def edit_category(request, category_id):
    """Edit a service category."""
    category = get_object_or_404(ServiceCategory, id=category_id)

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            category.name = form.cleaned_data['name']
            category.description = form.cleaned_data.get('description', '')
            category.save()
            messages.success(request, 'Category updated!')
            return redirect('custom_admin:service_categories')
    else:
        form = ServiceCategoryForm(initial={
            'name': category.name,
            'description': category.description,
        })

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'custom_admin/edit_category.html', context)


@admin_required
def toggle_category_status(request, category_id):
    """Activate or deactivate a category - POST only."""
    if request.method == 'POST':
        category = get_object_or_404(ServiceCategory, id=category_id)
        category.is_active = not category.is_active
        category.save()
        status = 'activated' if category.is_active else 'deactivated'
        messages.success(request, f'Category {status}.')
    return redirect('custom_admin:service_categories')


# ===================== AVAILABILITY MANAGEMENT =====================

@admin_required
def availability_list(request):
    """View vendor availability overview."""
    availabilities = VendorAvailability.objects.all().order_by('vendor__business_name', 'day_of_week')

    # Vendor filter
    vendor_id = request.GET.get('vendor', '')
    if vendor_id:
        availabilities = availabilities.filter(vendor_id=vendor_id)

    vendors = VendorProfile.objects.filter(verification_status='approved')

    context = {
        'availabilities': availabilities,
        'vendors': vendors,
        'selected_vendor': vendor_id,
    }
    return render(request, 'custom_admin/availability_list.html', context)
