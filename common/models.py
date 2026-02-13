"""
Complete Models - common/models.py
All shared models used by all actors
Based on project requirements sections 0-6
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# ==================== SECTION 1: TABLES (Base Entities) ====================

class Client(models.Model):
    """Client entity with balance and history tracking"""
    client_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    address = models.TextField(verbose_name="Address")
    city = models.CharField(max_length=100, verbose_name="City")
    postal_code = models.CharField(max_length=10, verbose_name="Postal Code")
    country = models.CharField(max_length=100, default='Algeria', verbose_name="Country")
    
    # Balance tracking
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Balance (DA)"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    def save(self, *args, **kwargs):
        if not self.client_id:
            last = Client.objects.all().order_by('id').last()
            if last:
                self.client_id = f"CLT{int(last.client_id[3:]) + 1:05d}"
            else:
                self.client_id = "CLT00001"
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'clients'
        ordering = ['-created_at']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f"{self.client_id} - {self.name}"


class Driver(models.Model):
    """Driver entity with availability and professional info"""
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('on_route', 'On Route'),
        ('off_duty', 'Off Duty'),
        ('on_leave', 'On Leave'),
    ]
    
    driver_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    
    # License information
    license_number = models.CharField(max_length=50, unique=True, verbose_name="License Number")
    license_expiry = models.DateField(null=True, blank=True, verbose_name="License Expiry")
    
    # Contact
    phone = models.CharField(max_length=20, verbose_name="Phone")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Address")
    
    # Professional info
    availability = models.CharField(
        max_length=20, 
        choices=AVAILABILITY_CHOICES, 
        default='available',
        verbose_name="Availability"
    )
    hire_date = models.DateField(verbose_name="Hire Date")
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Location tracking (for GPS tracking during deliveries)
    current_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="Current Latitude"
    )
    current_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="Current Longitude"
    )
    location_accuracy = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Location Accuracy (meters)"
    )
    last_location_timestamp = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Last Location Update"
    )
    
    def save(self, *args, **kwargs):
        if not self.driver_id:
            last = Driver.objects.all().order_by('id').last()
            if last:
                self.driver_id = f"DRV{int(last.driver_id[3:]) + 1:05d}"
            else:
                self.driver_id = "DRV00001"
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'drivers'
        ordering = ['last_name', 'first_name']
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
    
    def __str__(self):
        return f"{self.driver_id} - {self.first_name} {self.last_name}"


class Manager(models.Model):
    """Manager entity with professional information"""
    manager_id = models.CharField(max_length=20, unique=True, editable=False)

    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")

    department = models.CharField(max_length=100, verbose_name="Department")
    position = models.CharField(max_length=100, verbose_name="Position")
    hire_date = models.DateField(verbose_name="Hire Date")

    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")

    def save(self, *args, **kwargs):
        if not self.manager_id:
            last = Manager.objects.all().order_by('id').last()
            if last:
                self.manager_id = f"MGR{int(last.manager_id[3:]) + 1:05d}"
            else:
                self.manager_id = "MGR00001"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'managers'
        ordering = ['last_name', 'first_name']
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'

    def __str__(self):
        return f"{self.manager_id} - {self.first_name} {self.last_name}"


class Agent(models.Model):
    """Agent entity with professional information"""
    agent_id = models.CharField(max_length=20, unique=True, editable=False)

    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")

    department = models.CharField(max_length=100, verbose_name="Department")
    position = models.CharField(max_length=100, verbose_name="Position")
    hire_date = models.DateField(verbose_name="Hire Date")

    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")

    def save(self, *args, **kwargs):
        if not self.agent_id:
            last = Agent.objects.all().order_by('id').last()
            if last:
                self.agent_id = f"AGT{int(last.agent_id[3:]) + 1:05d}"
            else:
                self.agent_id = "AGT00001"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'agents'
        ordering = ['last_name', 'first_name']
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return f"{self.agent_id} - {self.first_name} {self.last_name}"


class Vehicle(models.Model):
    """Vehicle entity with capacity and status"""
    TYPE_CHOICES = [
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('out_of_service', 'Out of Service'),
    ]
    
    registration_number = models.CharField(max_length=20, unique=True, verbose_name="Registration Number")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    brand = models.CharField(max_length=100, verbose_name="Brand")
    model = models.CharField(max_length=100, verbose_name="Model")
    year = models.IntegerField(null=True, blank=True, verbose_name="Year")
    
    # Capacity
    capacity_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Capacity (kg)")
    capacity_m3 = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Capacity (m³)"
    )
    
    # Consumption
    fuel_consumption = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name="Fuel Consumption (L/100km)"
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        verbose_name="Status"
    )
    purchase_date = models.DateField(verbose_name="Purchase Date")
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="Last Maintenance")
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        db_table = 'vehicles'
        ordering = ['registration_number']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.registration_number} - {self.brand} {self.model}"


class Destination(models.Model):
    """Destination with base tariff for pricing"""
    ZONE_CHOICES = [
        ('local', 'Local'),
        ('national', 'National'),
        ('international', 'International'),
    ]
    
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    city = models.CharField(max_length=100, verbose_name="City")
    state = models.CharField(max_length=100, blank=True, verbose_name="State/Province") 
    country = models.CharField(max_length=100, default='Algeria', verbose_name="Country")
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, verbose_name="Zone")
    
    # Base tariff (Tarif de base)
    base_tariff = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Base Tariff (DA)",
        help_text="Fixed amount for this destination"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'destinations'
        ordering = ['country', 'city']
        unique_together = ['city', 'country']
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'
    
    def __str__(self):
        return f"{self.code} - {self.city}, {self.country}"


class ServiceType(models.Model):
    """Service type with pricing per weight and volume"""
    TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('international', 'International'),
    ]
    
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    name = models.CharField(max_length=100, verbose_name="Name")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Pricing (Tarification)
    weight_tariff = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Weight Tariff (DA/kg)",
        help_text="Price per kg"
    )
    volume_tariff = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Volume Tariff (DA/m³)",
        help_text="Price per m³"
    )
    
    # Delivery time
    delivery_time_days = models.IntegerField(
        verbose_name="Delivery Time (days)",
        help_text="Estimated delivery time"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_types'
        ordering = ['name']
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== SECTION 2: SHIPMENTS & TRACKING ====================

class Shipment(models.Model):
    """
    Shipment/Expedition with automatic pricing
    Formula: Montant total = Tarif de base + (Poids × Tarif poids) + (Volume × Tarif volume)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('at_sorting_center', 'At Sorting Center'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
        ('returned', 'Returned'),
    ]
    
    # Unique identifier
    shipment_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        verbose_name="Shipment Number"
    )
    
    # Relations
    client = models.ForeignKey(
        Client, 
        on_delete=models.PROTECT, 
        related_name='shipments',
        verbose_name="Client"
    )
    service_type = models.ForeignKey(
        ServiceType, 
        on_delete=models.PROTECT,
        verbose_name="Service Type"
    )
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.PROTECT,
        verbose_name="Destination"
    )
    
    # Package details
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Weight (kg)"
    )
    volume = models.DecimalField(
        max_digits=8, 
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name="Volume (m³)"
    )
    description = models.TextField(verbose_name="Description")
    
    # Automatic pricing
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        editable=False,
        verbose_name="Amount (DA)"
    )
    
    # Tracking
    status = models.CharField(
        max_length=30, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    estimated_delivery = models.DateField(null=True, blank=True, verbose_name="Estimated Delivery")
    actual_delivery = models.DateTimeField(null=True, blank=True, verbose_name="Actual Delivery")
    
    # Sender information
    sender_name = models.CharField(max_length=200, verbose_name="Sender Name")
    sender_phone = models.CharField(max_length=20, verbose_name="Sender Phone")
    sender_address = models.TextField(verbose_name="Sender Address")
    
    # Recipient information
    recipient_name = models.CharField(max_length=200, verbose_name="Recipient Name")
    recipient_phone = models.CharField(max_length=20, verbose_name="Recipient Phone")
    recipient_address = models.TextField(verbose_name="Recipient Address")
    
    # Additional
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shipments',
        verbose_name="Created By"
    )
    
    def save(self, *args, **kwargs):
        # Generate unique shipment number
        if not self.shipment_number:
            self.shipment_number = f"EXP{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate amount using formula
        if self.service_type and self.destination:
            self.amount = (
                self.destination.base_tariff +
                (self.weight * self.service_type.weight_tariff) +
                (self.volume * self.service_type.volume_tariff)
            )
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
    
    def __str__(self):
        return f"{self.shipment_number} - {self.client.name}"


class TrackingEvent(models.Model):
    """Tracking history for shipments"""
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='tracking_events',
        verbose_name="Shipment"
    )
    status = models.CharField(max_length=30, verbose_name="Status")
    location = models.CharField(max_length=200, verbose_name="Location")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Created By"
    )
    
    class Meta:
        db_table = 'tracking_events'
        ordering = ['-timestamp']
        verbose_name = 'Tracking Event'
        verbose_name_plural = 'Tracking Events'
    
    def __str__(self):
        return f"{self.shipment.shipment_number} - {self.status}"


class DeliveryTour(models.Model):
    """Delivery tour with driver, vehicle, and route data"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tour_number = models.CharField(max_length=20, unique=True, editable=False)
    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name='tours',
        verbose_name="Driver"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='tours',
        verbose_name="Vehicle"
    )
    date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Start Time")
    end_time = models.TimeField(null=True, blank=True, verbose_name="End Time")
    
    # Route data
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Distance (km)"
    )
    fuel_consumed = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Fuel Consumed (L)"
    )
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Duration (hours)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name="Status"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Created By"
    )
    
    def save(self, *args, **kwargs):
        if not self.tour_number:
            last = DeliveryTour.objects.all().order_by('id').last()
            if last:
                self.tour_number = f"TOUR{int(last.tour_number[4:]) + 1:06d}"
            else:
                self.tour_number = "TOUR000001"
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'delivery_tours'
        ordering = ['-date', '-created_at']
        verbose_name = 'Delivery Tour'
        verbose_name_plural = 'Delivery Tours'
    
    def __str__(self):
        return f"{self.tour_number} - {self.driver}"


class TourShipment(models.Model):
    """Link between tours and shipments"""
    tour = models.ForeignKey(
        DeliveryTour,
        on_delete=models.CASCADE,
        related_name='tour_shipments'
    )
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='tour_assignments'
    )
    sequence = models.IntegerField(verbose_name="Sequence")
    delivered = models.BooleanField(default=False)
    delivery_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tour_shipments'
        ordering = ['tour', 'sequence']
        unique_together = ['tour', 'shipment']


# ==================== SECTION 3: INVOICING & PAYMENTS ====================

class Invoice(models.Model):
    """
    Invoice with automatic tax calculation
    Montant TTC = Montant HT + Montant TVA
    TVA = 19%
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Amounts
    amount_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tva_rate = models.DecimalField(max_digits=5, decimal_places=2, default=19.00)
    amount_tva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.all().order_by('id').last()
            if last:
                self.invoice_number = f"FAC{int(last.invoice_number[3:]) + 1:07d}"
            else:
                self.invoice_number = "FAC0000001"
        
        # Calculate amounts
        self.amount_tva = self.amount_ht * (self.tva_rate / 100)
        self.amount_ttc = self.amount_ht + self.amount_tva
        
        # Update status based on payment
        if self.amount_paid >= self.amount_ttc:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        
        super().save(*args, **kwargs)
    
    @property
    def balance_due(self):
        return self.amount_ttc - self.amount_paid
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


class InvoiceLine(models.Model):
    """Invoice line items"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'invoice_lines'
        unique_together = ['invoice', 'shipment']


class Payment(models.Model):
    """Payment tracking"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('ccp', 'CCP'),
    ]
    
    payment_number = models.CharField(max_length=20, unique=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            last = Payment.objects.all().order_by('id').last()
            if last:
                self.payment_number = f"PAY{int(last.payment_number[3:]) + 1:07d}"
            else:
                self.payment_number = "PAY0000001"
        
        super().save(*args, **kwargs)
        
        # Update invoice paid amount
        self.invoice.amount_paid = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.save()
        
        # Update client balance if partial payment
        if self.invoice.balance_due > 0:
            self.invoice.client.balance = self.invoice.balance_due
            self.invoice.client.save()
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']


# ==================== SECTION 4: INCIDENTS ====================

class Incident(models.Model):
    """Incident management"""
    TYPE_CHOICES = [
        ('delay', 'Delay'),
        ('loss', 'Loss'),
        ('damage', 'Damage'),
        ('technical', 'Technical Problem'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    incident_number = models.CharField(max_length=20, unique=True, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    tour = models.ForeignKey(DeliveryTour, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        if not self.incident_number:
            last = Incident.objects.all().order_by('id').last()
            if last:
                self.incident_number = f"INC{int(last.incident_number[3:]) + 1:06d}"
            else:
                self.incident_number = "INC000001"
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'incidents'
        ordering = ['-reported_date']


# ==================== SECTION 5: CLAIMS ====================

class Claim(models.Model):
    """Customer claims management"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    claim_number = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='claims')
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='claims')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='claims')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    filed_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_claims')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_claims')
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            last = Claim.objects.all().order_by('id').last()
            if last:
                self.claim_number = f"REC{int(last.claim_number[3:]) + 1:06d}"
            else:
                self.claim_number = "REC000001"
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'claims'
        ordering = ['-filed_date']


# ==================== SECTION 0: FAVORITES ====================

class Favorite(models.Model):
    """User favorites for quick access"""
    FEATURE_CHOICES = [
        ('create_shipment', 'Create Shipment'),
        ('create_tour', 'Create Tour'),
        ('create_invoice', 'Create Invoice'),
        ('track_shipment', 'Track Shipment'),
        ('view_tours', 'View Tours'),
        ('view_clients', 'View Clients'),
        ('view_incidents', 'View Incidents'),
        ('view_claims', 'View Claims'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        ordering = ['order']
        unique_together = ['user', 'feature']


# ==================== AUDIT LOG ====================

class AuditLog(models.Model):
    """Audit log for security and tracking sensitive actions"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="User"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    model_name = models.CharField(max_length=100, verbose_name="Model")
    object_id = models.CharField(max_length=50, verbose_name="Object ID")
    details = models.TextField(blank=True, verbose_name="Details")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.user} - {self.action} {self.model_name} at {self.timestamp}"