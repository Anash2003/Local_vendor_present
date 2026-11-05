"""
Customer views - dashboard, browsing, booking, profile.
All views use @customer_required decorator for access control.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from accounts.decorators import customer_required
from accounts.models import VendorProfile
from services.models import Service, ServiceCategory, Booking, VendorAvailability
from .forms import CustomerProfileEditForm, BookingForm


@customer_required
def customer_dashboard(request):
    """Customer dashboard with overview stats."""
    profile = request.user.customer_profile
    bookings = Booking.objects.filter(customer=profile)

    context = {
        'profile': profile,
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'recent_bookings': bookings[:5],
    }
    return render(request, 'customer/dashboard.html', context)


@customer_required
def browse_vendors(request):
    """Browse all approved and active vendors."""
    # Only show approved and active vendors
    vendors = VendorProfile.objects.filter(
        verification_status='approved',
        is_active_vendor=True
    )

    # Search filter
    search = request.GET.get('search', '')
    if search:
        vendors = vendors.filter(business_name__icontains=search)

    # City filter
    city = request.GET.get('city', '')
    if city:
        vendors = vendors.filter(city__icontains=city)

    context = {
        'vendors': vendors,
        'search': search,
        'city': city,
    }
    return render(request, 'customer/browse_vendors.html', context)


@customer_required
def vendor_detail(request, vendor_id):
    """View details of a specific approved vendor."""
    # Only allow viewing approved, active vendors
    vendor = get_object_or_404(
        VendorProfile,
        id=vendor_id,
        verification_status='approved',
        is_active_vendor=True
    )
    services = Service.objects.filter(vendor=vendor, is_available=True)
    availability = VendorAvailability.objects.filter(vendor=vendor, is_available=True)

    context = {
        'vendor': vendor,
        'services': services,
        'availability': availability,
    }
    return render(request, 'customer/vendor_detail.html', context)


@customer_required
def browse_services(request):
    """Browse all available services from approved vendors."""
    services = Service.objects.filter(
        is_available=True,
        vendor__verification_status='approved',
        vendor__is_active_vendor=True
    )

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        services = services.filter(category_id=category_id)

    # Search filter
    search = request.GET.get('search', '')
    if search:
        services = services.filter(name__icontains=search)

    categories = ServiceCategory.objects.filter(is_active=True)

    context = {
        'services': services,
        'categories': categories,
        'selected_category': category_id,
        'search': search,
    }
    return render(request, 'customer/browse_services.html', context)


@customer_required
def book_service(request, service_id):
    """Book a service - check availability before creating booking."""
    service = get_object_or_404(
        Service,
        id=service_id,
        is_available=True,
        vendor__verification_status='approved',
        vendor__is_active_vendor=True
    )
    profile = request.user.customer_profile

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            booking_time = form.cleaned_data['booking_time']

            # Check vendor availability for the selected day
            day_name = booking_date.strftime('%A').lower()
            availability = VendorAvailability.objects.filter(
                vendor=service.vendor,
                day_of_week=day_name,
                is_available=True
            ).first()

            if not availability:
                messages.error(request, 'The vendor is not available on this day.')
                return render(request, 'customer/book_service.html', {
                    'form': form, 'service': service
                })

            # Check if time is within vendor's available hours
            if booking_time < availability.start_time or booking_time > availability.end_time:
                messages.error(
                    request,
                    f'Please select a time between {availability.start_time.strftime("%I:%M %p")} '
                    f'and {availability.end_time.strftime("%I:%M %p")}.'
                )
                return render(request, 'customer/book_service.html', {
                    'form': form, 'service': service
                })

            # Create booking
            Booking.objects.create(
                customer=profile,
                vendor=service.vendor,
                service=service,
                booking_date=booking_date,
                booking_time=booking_time,
                notes=form.cleaned_data.get('notes', ''),
                status='pending',
            )

            messages.success(request, 'Booking created successfully! Waiting for vendor confirmation.')
            return redirect('customer:my_bookings')
    else:
        form = BookingForm()

    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'customer/book_service.html', context)


@customer_required
def my_bookings(request):
    """View customer's own bookings only."""
    profile = request.user.customer_profile
    # Only this customer's bookings - ownership check
    bookings = Booking.objects.filter(customer=profile)

    # Status filter
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)

    context = {
        'bookings': bookings,
        'selected_status': status,
    }
    return render(request, 'customer/my_bookings.html', context)


@customer_required
def booking_detail(request, booking_id):
    """View a specific booking - ownership verified."""
    profile = request.user.customer_profile
    # Ownership check: only this customer's booking
    booking = get_object_or_404(Booking, id=booking_id, customer=profile)

    context = {
        'booking': booking,
    }
    return render(request, 'customer/booking_detail.html', context)


@customer_required
def cancel_booking(request, booking_id):
    """Cancel a pending booking - POST only."""
    if request.method == 'POST':
        profile = request.user.customer_profile
        # Ownership check
        booking = get_object_or_404(Booking, id=booking_id, customer=profile)

        if booking.status == 'pending':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking cancelled successfully.')
        else:
            messages.error(request, 'Only pending bookings can be cancelled.')

    return redirect('customer:my_bookings')


@customer_required
def customer_profile(request):
    """View customer profile."""
    profile = request.user.customer_profile
    context = {
        'profile': profile,
    }
    return render(request, 'customer/profile.html', context)


@customer_required
def edit_profile(request):
    """Edit customer profile."""
    profile = request.user.customer_profile

    if request.method == 'POST':
        form = CustomerProfileEditForm(request.POST)
        if form.is_valid():
            # Update User fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            # Update Profile fields
            profile.phone = form.cleaned_data['phone']
            profile.address = form.cleaned_data.get('address', '')
            profile.city = form.cleaned_data['city']
            profile.state = form.cleaned_data['state']
            profile.pincode = form.cleaned_data['pincode']
            profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('customer:profile')
    else:
        # Pre-populate form with existing data
        form = CustomerProfileEditForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'pincode': profile.pincode,
        })

    context = {
        'form': form,
    }
    return render(request, 'customer/edit_profile.html', context)
