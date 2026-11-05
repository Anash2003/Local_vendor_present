from django.contrib import admin
from .models import ServiceCategory, Service, VendorAvailability, Booking

admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(VendorAvailability)
admin.site.register(Booking)
