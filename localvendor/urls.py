"""Main URL configuration for localvendor project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django's built-in admin (for debugging only)
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('customer/', include('customer.urls')),
    path('vendor/', include('vendor.urls')),
    path('admin/', include('custom_admin.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
