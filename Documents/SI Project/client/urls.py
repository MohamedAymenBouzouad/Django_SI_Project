from django.urls import path
from . import views

app_name = 'client'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.client_dashboard, name='dashboard'),

    # Shipments
    path('shipments/', views.shipment_list, name='shipment_list'),
    path('shipments/<int:shipment_id>/', views.shipment_detail, name='shipment_detail'),
    path('track/', views.track_shipment, name='track_shipment'),

    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),

    # Claims
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claims/submit/', views.submit_claim, name='submit_claim'),

    # Profile
    path('profile/', views.client_profile, name='profile'),
]