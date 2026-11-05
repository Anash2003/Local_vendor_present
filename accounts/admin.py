from django.contrib import admin
from .models import User, CustomerProfile, VendorProfile, VendorDocument

admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(VendorProfile)
admin.site.register(VendorDocument)
