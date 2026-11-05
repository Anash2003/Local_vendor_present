"""
Vendor views - dashboard, services, availability, bookings, profile.
All views use @vendor_required (checks approved status).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from accounts.decorators import vendor_required
from services.models import Service, ServiceCategory, Booking, VendorAvailability
from .forms import VendorProfileEditForm, ServiceForm, AvailabilityForm


@vendor_required
def vendor_dashboard(request):
    """Vendor dashboard with overview stats."""
    vendor = request.user.vendor_profile
    bookings = Booking.objects.filter(vendor=vendor)

    context = {
        'vendor': vendor,
        'total_services': Service.objects.filter(vendor=vendor).count(),
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'upcoming_bookings_count': bookings.filter(
            status='confirmed', booking_date__gte=date.today()
        ).count(),
        'recent_bookings': bookings[:5],
    }
    return render(request, 'vendor/dashboard.html', context)


@vendor_required
def my_services(request):
    """List vendor's own services only."""
    vendor = request.user.vendor_profile
    # Ownership: only this vendor's services
    services = Service.objects.filter(vendor=vendor)

    context = {
        'services': services,
    }
    return render(request, 'vendor/my_services.html', context)


@vendor_required
def add_service(request):
    """Add a new service."""
    vendor = request.user.vendor_profile

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = vendor  # Set vendor to current user
            service.save()
            messages.success(request, 'Service added successfully!')
            return redirect('vendor:my_services')
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'action': 'Add',
    }
    return render(request, 'vendor/service_form.html', context)


@vendor_required
def edit_service(request, service_id):
    """Edit an existing service - ownership verified."""
    vendor = request.user.vendor_profile
    # Ownership check: only this vendor's service
    service = get_object_or_404(Service, id=service_id, vendor=vendor)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('vendor:my_services')
    else:
        form = ServiceForm(instance=service)

    context = {
        'form': form,
        'action': 'Edit',
        'service': service,
    }
    return render(request, 'vendor/service_form.html', context)


@vendor_required
def delete_service(request, service_id):
    """Delete a service - POST only, ownership verified."""
    if request.method == 'POST':
        vendor = request.user.vendor_profile
        service = get_object_or_404(Service, id=service_id, vendor=vendor)
        service.delete()
        messages.success(request, 'Service deleted successfully!')
    return redirect('vendor:my_services')


@vendor_required
def manage_availability(request):
    """Manage vendor availability - add/update for each day."""
    vendor = request.user.vendor_profile
    current_availability = VendorAvailability.objects.filter(vendor=vendor)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            day = form.cleaned_data['day_of_week']
            # Update or create availability for this day
            VendorAvailability.objects.update_or_create(
                vendor=vendor,
                day_of_week=day,
                defaults={
                    'start_time': form.cleaned_data['start_time'],
                    'end_time': form.cleaned_data['end_time'],
                    'is_available': form.cleaned_data.get('is_available', True),
                }
            )
            messages.success(request, f'Availability for {day.capitalize()} updated!')
            return redirect('vendor:availability')
    else:
        form = AvailabilityForm()

    context = {
        'form': form,
        'current_availability': current_availability,
    }
    return render(request, 'vendor/availability.html', context)


@vendor_required
def delete_availability(request, availability_id):
    """Delete an availability slot - POST only, ownership verified."""
    if request.method == 'POST':
        vendor = request.user.vendor_profile
        availability = get_object_or_404(VendorAvailability, id=availability_id, vendor=vendor)
        availability.delete()
        messages.success(request, 'Availability removed.')
    return redirect('vendor:availability')


@vendor_required
def received_bookings(request):
    """View pending bookings received by this vendor."""
    vendor = request.user.vendor_profile
    bookings = Booking.objects.filter(vendor=vendor, status='pending')

    context = {
        'bookings': bookings,
        'title': 'Received Bookings',
    }
    return render(request, 'vendor/bookings_list.html', context)


@vendor_required
def upcoming_bookings(request):
    """View confirmed upcoming bookings."""
    vendor = request.user.vendor_profile
    bookings = Booking.objects.filter(
        vendor=vendor,
        status='confirmed',
        booking_date__gte=date.today()
    ).order_by('booking_date', 'booking_time')

    context = {
        'bookings': bookings,
        'title': 'Upcoming Bookings',
    }
    return render(request, 'vendor/bookings_list.html', context)


@vendor_required
def booking_detail(request, booking_id):
    """View booking detail - ownership verified."""
    vendor = request.user.vendor_profile
    booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)

    context = {
        'booking': booking,
    }
    return render(request, 'vendor/booking_detail.html', context)


@vendor_required
def accept_booking(request, booking_id):
    """Accept a pending booking - POST only."""
    if request.method == 'POST':
        vendor = request.user.vendor_profile
        booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)

        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, 'Booking accepted!')
        else:
            messages.error(request, 'Only pending bookings can be accepted.')

    return redirect('vendor:received_bookings')


@vendor_required
def reject_booking(request, booking_id):
    """Reject a booking with reason - POST only."""
    if request.method == 'POST':
        vendor = request.user.vendor_profile
        booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)

        if booking.status == 'pending':
            booking.status = 'rejected'
            booking.rejection_reason = request.POST.get('rejection_reason', '')
            booking.save()
            messages.success(request, 'Booking rejected.')
        else:
            messages.error(request, 'Only pending bookings can be rejected.')

    return redirect('vendor:received_bookings')


@vendor_required
def complete_booking(request, booking_id):
    """Mark a confirmed booking as completed - POST only."""
    if request.method == 'POST':
        vendor = request.user.vendor_profile
        booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)

        if booking.status == 'confirmed':
            booking.status = 'completed'
            booking.save()
            messages.success(request, 'Booking marked as completed!')
        else:
            messages.error(request, 'Only confirmed bookings can be marked as completed.')

    return redirect('vendor:upcoming_bookings')


@vendor_required
def vendor_profile(request):
    """View vendor profile."""
    vendor = request.user.vendor_profile
    context = {
        'vendor': vendor,
    }
    return render(request, 'vendor/profile.html', context)


@vendor_required
def edit_profile(request):
    """Edit vendor profile and business details."""
    vendor = request.user.vendor_profile

    if request.method == 'POST':
        form = VendorProfileEditForm(request.POST)
        if form.is_valid():
            # Update User fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # Update Vendor Profile fields
            vendor.phone = form.cleaned_data['phone']
            vendor.business_name = form.cleaned_data['business_name']
            vendor.business_description = form.cleaned_data.get('business_description', '')
            vendor.business_address = form.cleaned_data['business_address']
            vendor.city = form.cleaned_data['city']
            vendor.state = form.cleaned_data['state']
            vendor.pincode = form.cleaned_data['pincode']
            vendor.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('vendor:profile')
    else:
        form = VendorProfileEditForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
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
    }
    return render(request, 'vendor/edit_profile.html', context)
