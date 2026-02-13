from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.manager_dashboard, name='dashboard'),

    # Analytics
    path('analytics/commercial/', views.commercial_analytics, name='commercial_analytics'),
    path('analytics/operational/', views.operational_analytics, name='operational_analytics'),

    # Management Views
    path('shipments/', views.shipment_management, name='shipment_management'),
    path('clients/', views.client_management, name='client_management'),
    path('drivers/', views.driver_management, name='driver_management'),
    path('incidents/', views.incident_management, name='incident_management'),
    path('tours/', views.tour_management, name='tour_management'),

    # Reports
    path('reports/', views.system_reports, name='system_reports'),
]