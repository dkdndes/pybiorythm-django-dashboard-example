"""
URL configuration for PyBiorythm Dashboard project.

Django dashboard application that consumes PyBiorythm REST API and presents
interactive Plotly visualizations using Django + HTMX for dynamic updates.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
