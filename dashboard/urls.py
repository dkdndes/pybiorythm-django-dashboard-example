"""
URL configuration for the PyBiorythm dashboard app.

Defines URL patterns for the dashboard views including main dashboard,
person-specific views, and HTMX endpoints for dynamic chart updates.
"""

from django.urls import path
from . import views
from .test_view import test_chart_view

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard views
    path('', views.dashboard_home, name='home'),
    path('person/<int:person_id>/', views.person_dashboard, name='person_dashboard'),
    
    # Chart API endpoints for HTMX
    path('charts/person/<int:person_id>/line/', views.chart_biorhythm_line, name='chart_line'),
    path('charts/person/<int:person_id>/distribution/', views.chart_distribution, name='chart_distribution'),
    path('charts/person/<int:person_id>/critical/', views.chart_critical_days, name='chart_critical'),
    path('charts/person/<int:person_id>/phases/', views.chart_cycle_phases, name='chart_phases'),
    path('charts/person/<int:person_id>/correlation/', views.chart_correlation, name='chart_correlation'),
    path('charts/person/<int:person_id>/stats/', views.chart_statistics, name='chart_statistics'),
    
    # Action endpoints
    path('person/<int:person_id>/calculate/', views.calculate_biorhythm, name='calculate_biorhythm'),
    
    # HTMX partial endpoints
    path('api/status/', views.api_status, name='api_status'),
    path('partials/people/', views.people_list_partial, name='people_list_partial'),
    path('partials/person/<int:person_id>/', views.person_info_partial, name='person_info_partial'),
    
    # Test endpoint
    path('test-chart/', test_chart_view, name='test_chart'),
    path('test-correlation/', views.test_correlation_view, name='test_correlation'),
    path('test-correlation-page/', views.test_correlation_page, name='test_correlation_page'),
    path('test-simple-correlation/', views.test_simple_correlation_view, name='test_simple_correlation'),
    path('debug-correlation-data/', views.debug_correlation_data, name='debug_correlation_data'),
    path('test-exact-correlation/', views.test_exact_correlation, name='test_exact_correlation'),
]