from django.urls import path
from . import views

app_name = 'driver'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.driver_dashboard, name='dashboard'),

    # Tours
    path('tours/', views.tour_list, name='tour_list'),
    path('tours/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tours/<int:tour_id>/start/', views.start_tour, name='start_tour'),
    path('tours/<int:tour_id>/complete/', views.complete_tour, name='complete_tour'),

    # Shipments
    path('shipments/<int:shipment_id>/update-status/', views.update_shipment_status, name='update_shipment_status'),
    path('shipments/<int:shipment_id>/tracking/add/', views.add_tracking_event, name='add_tracking'),

    # Incidents
    path('incidents/report/', views.report_incident, name='report_incident'),
    path('incidents/report/<int:shipment_id>/', views.report_incident, name='report_incident_shipment'),

    # Location tracking
    path('location/update/', views.update_location, name='update_location'),
]