from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.agent_dashboard, name='dashboard'),

    # Section 0: Favorites
    path('favorites/', views.manage_favorites, name='favorites'),

    # Section 1: Tables (CRUD)
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.delete_client, name='client_delete'),

    path('drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('destinations/', views.DestinationListView.as_view(), name='destination_list'),
    path('service-types/', views.ServiceTypeListView.as_view(), name='service_type_list'),

    # Section 2: Shipments & Tracking
    path('shipments/create/', views.create_shipment, name='create_shipment'),
    path('shipments/', views.ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    path('shipments/<int:shipment_id>/tracking/add/', views.add_tracking_event, name='add_tracking'),

    # Delivery Tours
    path('tours/create/', views.create_delivery_tour, name='create_tour'),
    path('tours/', views.DeliveryTourListView.as_view(), name='tour_list'),
    path('tours/<int:pk>/', views.DeliveryTourListView.as_view(), name='tour_detail'),

    # Section 3: Invoicing
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/', views.ShipmentListView.as_view(), name='invoice_list'),  # Reuse shipment list for now
    path('invoices/<int:pk>/', views.ShipmentDetailView.as_view(), name='invoice_detail'),  # Reuse shipment detail
    path('api/client-shipments/', views.get_client_shipments, name='client_shipments_api'),

    # Section 4: Incidents
    path('incidents/report/', views.report_incident, name='report_incident'),
    path('incidents/', views.ShipmentListView.as_view(), name='incident_list'),  # Reuse shipment list
    path('incidents/<int:pk>/', views.ShipmentDetailView.as_view(), name='incident_detail'),  # Reuse shipment detail

    # Section 5: Claims
    path('claims/', views.manage_claims, name='claims'),
    path('claims/<int:claim_id>/update/', views.update_claim_status, name='update_claim'),
]