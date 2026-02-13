from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, Sum
from common.models import (
    Client, Driver, Vehicle, Destination, ServiceType, Shipment,
    Invoice, Payment, Incident, Claim, Favorite, DeliveryTour,
    TrackingEvent
)
import json

# ==================== DASHBOARD ====================

def agent_dashboard(request):
    """Agent dashboard with system overview"""
    if not request.user.is_authenticated or request.user.role != 'agent':
        return redirect('/auth/agent/login/')

    # Get recent activities
    context = {
        'recent_shipments': Shipment.objects.all().order_by('-created_at')[:5],
        'pending_shipments': Shipment.objects.filter(status='created').count(),
        'active_tours': DeliveryTour.objects.filter(status='in_progress').count(),
        'pending_invoices': Invoice.objects.filter(status__in=['sent', 'overdue']).count(),
        'open_incidents': Incident.objects.filter(status__in=['reported', 'investigating']).count(),
        'user': request.user
    }

    return render(request, 'agent/dashboard.html', context)

# ==================== SECTION 0: FAVORITES ====================

def manage_favorites(request):
    """AG-00-01 to AG-00-04: Manage favorite features"""
    if not request.user.is_authenticated or request.user.role != 'agent':
        return redirect('/auth/agent/login/')

    if request.method == 'POST':
        action = request.POST.get('action')
        feature = request.POST.get('feature')

        if action == 'add':
            Favorite.objects.get_or_create(
                user_id=request.session['user_id'],
                feature=feature,
                defaults={'order': Favorite.objects.filter(user_id=request.session['user_id']).count()}
            )
        elif action == 'remove':
            Favorite.objects.filter(user_id=request.session['user_id'], feature=feature).delete()
        elif action == 'reorder':
            order_data = json.loads(request.POST.get('order_data', '{}'))
            for feature, order in order_data.items():
                Favorite.objects.filter(user_id=request.session['user_id'], feature=feature).update(order=order)

        return JsonResponse({'success': True})

    favorites = Favorite.objects.filter(user_id=request.session['user_id']).order_by('order')
    return render(request, 'agent/favorites.html', {'favorites': favorites})

# ==================== SECTION 1: TABLES (CRUD) ====================

class ClientListView(ListView):
    """AG-01-01: View Client table"""
    model = Client
    template_name = 'agent/client_list.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

class ClientCreateView(CreateView):
    """AG-01-01: Create Client"""
    model = Client
    template_name = 'agent/client_form.html'
    fields = ['name', 'email', 'phone', 'address', 'city', 'postal_code', 'country']
    success_url = reverse_lazy('agent:client_list')

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Client created successfully!')
        return super().form_valid(form)

class ClientUpdateView(UpdateView):
    """AG-01-01: Update Client"""
    model = Client
    template_name = 'agent/client_form.html'
    fields = ['name', 'email', 'phone', 'address', 'city', 'postal_code', 'country']
    success_url = reverse_lazy('agent:client_list')

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Client updated successfully!')
        return super().form_valid(form)

def delete_client(request, pk):
    """AG-01-01: Delete Client"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    client = get_object_or_404(Client, pk=pk)
    client.delete()
    messages.success(request, 'Client deleted successfully!')
    return redirect('agent:client_list')

# Similar CRUD views for Driver, Vehicle, Destination, ServiceType
class DriverListView(ListView):
    model = Driver
    template_name = 'agent/driver_list.html'
    paginate_by = 20

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'agent/vehicle_list.html'
    paginate_by = 20

class DestinationListView(ListView):
    model = Destination
    template_name = 'agent/destination_list.html'
    paginate_by = 20

class ServiceTypeListView(ListView):
    model = ServiceType
    template_name = 'agent/service_type_list.html'
    paginate_by = 20

# ==================== SECTION 2: SHIPMENTS & TRACKING ====================

def create_shipment(request):
    """AG-02-01: Create shipment with automatic pricing"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    if request.method == 'POST':
        client_id = request.POST.get('client')
        service_type_id = request.POST.get('type')
        destination_id = request.POST.get('destination')
        weight = float(request.POST.get('weight', 0))
        volume = float(request.POST.get('volume', 0))
        description = request.POST.get('description', '')

        # Simple pricing calculation (in real app, this would use the Pricing model)
        # Base rate + weight rate + volume rate
        base_rate = 10.0  # Base delivery rate
        weight_rate = 2.0  # Per kg
        volume_rate = 5.0  # Per cubic meter

        amount = base_rate + (weight * weight_rate) + (volume * volume_rate)

        # Create shipment
        shipment = Shipment.objects.create(
            client_id=client_id,
            service_type_id=service_type_id,
            destination_id=destination_id,
            weight=weight,
            volume=volume,
            description=description,
            amount=amount
        )

        # Create initial tracking event
        TrackingEvent.objects.create(
            shipment=shipment,
            status='created',
            notes='Shipment created by agent'
        )

        messages.success(request, f'Shipment {shipment.tracking_number} created successfully!')
        return redirect('agent:shipment_detail', pk=shipment.id)

    # GET request
    clients = Client.objects.all()
    service_types = ServiceType.objects.filter(is_active=True)
    destinations = Destination.objects.filter(is_active=True)

    return render(request, 'agent/create_shipment.html', {
        'clients': clients,
        'service_types': service_types,
        'destinations': destinations
    })

class ShipmentListView(ListView):
    """AG-02-06: View shipment journal"""
    model = Shipment
    template_name = 'agent/shipment_list.html'
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Shipment.objects.select_related('client', 'destination', 'service_type')

        # Filters
        status = self.request.GET.get('status')
        client_id = self.request.GET.get('client')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if status:
            queryset = queryset.filter(status=status)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by('-created_at')

class ShipmentDetailView(DetailView):
    """AG-02-07: View shipment tracking"""
    model = Shipment
    template_name = 'agent/shipment_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_history'] = self.object.tracking_history.all().order_by('-timestamp')
        return context

def add_tracking_event(request, shipment_id):
    """AG-02-09: Add tracking event manually"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    shipment = get_object_or_404(Shipment, id=shipment_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        location = request.POST.get('location', '')
        notes = request.POST.get('notes', '')

        TrackingEvent.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            notes=notes
        )

        # Update shipment status if needed
        if status in ['delivered', 'failed_delivery']:
            shipment.status = status
            if status == 'delivered':
                shipment.actual_delivery_date = timezone.now()
            shipment.save()

        messages.success(request, 'Tracking event added successfully!')
        return redirect('agent:shipment_detail', pk=shipment_id)

    return render(request, 'agent/add_tracking.html', {'shipment': shipment})

# ==================== DELIVERY TOURS ====================

def create_delivery_tour(request):
    """AG-02-10: Create delivery tour"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    if request.method == 'POST':
        driver_id = request.POST.get('driver')
        vehicle_id = request.POST.get('vehicle')
        planned_date = request.POST.get('planned_date')
        shipment_ids = request.POST.getlist('shipments')

        # Create tour
        tour = DeliveryTour.objects.create(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            planned_date=planned_date,
            total_shipments=len(shipment_ids)
        )

        # Assign shipments to tour
        for shipment_id in shipment_ids:
            shipment = Shipment.objects.get(id=shipment_id)
            shipment.assigned_tour = tour
            shipment.save()

        messages.success(request, f'Delivery tour created successfully!')
        return redirect('agent:tour_detail', pk=tour.id)

    # GET request
    drivers = Driver.objects.filter(is_active=True)
    vehicles = Vehicle.objects.filter(is_active=True)
    available_shipments = Shipment.objects.filter(
        status__in=['created', 'in_transit'],
        assigned_tour__isnull=True
    )

    return render(request, 'agent/create_tour.html', {
        'drivers': drivers,
        'vehicles': vehicles,
        'available_shipments': available_shipments
    })

class DeliveryTourListView(ListView):
    """AG-02-14: View tours journal"""
    model = DeliveryTour
    template_name = 'agent/tour_list.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
            return redirect('/auth/agent/login/')
        return super().dispatch(request, *args, **kwargs)

# ==================== INVOICING ====================

def create_invoice(request):
    """AG-03-01: Generate invoice from shipments"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    if request.method == 'POST':
        client_id = request.POST.get('client')
        shipment_ids = request.POST.getlist('shipments')

        client = get_object_or_404(Client, id=client_id)

        # Create invoice
        invoice = Invoice.objects.create(
            client=client,
            issue_date=timezone.now().date()
        )

        total_amount = 0
        for shipment_id in shipment_ids:
            shipment = Shipment.objects.get(id=shipment_id)
            # Create invoice line (simplified - in real app you'd have InvoiceLine model)
            total_amount += shipment.amount_ttc

        invoice.total_ttc = total_amount
        invoice.save()

        messages.success(request, f'Invoice created successfully!')
        return redirect('agent:invoice_detail', pk=invoice.id)

    # GET request
    clients = Client.objects.all()
    return render(request, 'agent/create_invoice.html', {'clients': clients})

def get_client_shipments(request):
    """AJAX: Get shipments for a client that can be invoiced"""
    client_id = request.GET.get('client_id')
    shipments = Shipment.objects.filter(
        client_id=client_id,
        status='delivered'
    ).exclude(invoice_items__isnull=False)  # Not already invoiced

    data = []
    for shipment in shipments:
        data.append({
            'id': shipment.id,
            'tracking_number': shipment.tracking_number,
            'amount': float(shipment.amount_ttc),
            'description': f"Shipment {shipment.tracking_number}"
        })

    return JsonResponse({'shipments': data})

# ==================== INCIDENTS ====================

def report_incident(request):
    """AG-04-01: Report incident"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    if request.method == 'POST':
        shipment_id = request.POST.get('shipment')
        tour_id = request.POST.get('tour')
        incident_type = request.POST.get('type')
        description = request.POST.get('description')
        location = request.POST.get('location', '')

        incident = Incident.objects.create(
            type=incident_type,
            title=f"Incident reported by agent",
            description=description,
            location=location,
            shipment_id=shipment_id if shipment_id else None,
            tour_id=tour_id if tour_id else None
        )

        messages.success(request, 'Incident reported successfully!')
        return redirect('agent:incident_detail', pk=incident.id)

    # GET request
    shipments = Shipment.objects.all()[:50]  # Recent shipments
    tours = DeliveryTour.objects.filter(status__in=['planned', 'in_progress'])

    return render(request, 'agent/report_incident.html', {
        'shipments': shipments,
        'tours': tours
    })

# ==================== CLAIMS ====================

def manage_claims(request):
    """AG-05-01 to AG-05-05: Claims management"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    claims = Claim.objects.all().order_by('-filed_date')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        claims = claims.filter(status=status)

    paginator = Paginator(claims, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'agent/claims.html', {
        'page_obj': page_obj,
        'status_filter': status
    })

def update_claim_status(request, claim_id):
    """AG-05-03: Update claim status"""
    if 'user_id' not in request.session or request.session.get('user_role') != 'agent':
        return redirect('/auth/agent/login/')

    claim = get_object_or_404(Claim, id=claim_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        resolution = request.POST.get('resolution', '')

        claim.status = new_status
        if resolution:
            claim.resolution = resolution
            claim.resolution_date = timezone.now()
        claim.save()

        messages.success(request, f'Claim status updated to {new_status}!')
        return redirect('agent:claims')

    return render(request, 'agent/update_claim.html', {'claim': claim})