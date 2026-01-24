from django.contrib import admin

# Register your models here.
from .models import Client, Driver, Vehicle, Destination, ServiceType, Shipment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'name', 'email', 'phone', 'balance']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['driver_id', 'first_name', 'last_name', 'availability']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'type', 'status']

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['code', 'city', 'country', 'base_tariff']

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type']

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'client', 'status', 'amount']