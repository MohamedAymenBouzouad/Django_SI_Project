from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q, Avg, Max
from django.utils import timezone
from datetime import timedelta, date
from common.models import (
    Shipment, Client, Driver, Invoice, Incident, DeliveryTour,
    Claim, ServiceType, Destination, Vehicle, TourShipment
)
from authentication.models import User

def get_manager_from_request(request):
    """Helper function to get manager from authenticated user"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return None
    return request.user

# ==================== MANAGER DASHBOARD ====================

def manager_dashboard(request):
    """MG-01 to MG-09: Comprehensive analytics dashboard"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    # Get comprehensive system stats
    stats = get_system_stats()

    # Recent activities
    recent_shipments = Shipment.objects.all().order_by('-created_at')[:10]
    recent_incidents = Incident.objects.filter(
        status__in=['reported', 'investigating']
    ).order_by('-reported_date')[:5]

    context = {
        'manager': manager,
        'system_stats': stats,
        'recent_shipments': recent_shipments,
        'recent_incidents': recent_incidents,
    }

    return render(request, 'manager/dashboard.html', context)

def get_system_stats():
    """Get comprehensive system statistics"""
    # Shipment stats
    shipments = Shipment.objects.all()
    total_shipments = shipments.count()
    delivered_shipments = shipments.filter(status='delivered').count()
    in_transit_shipments = shipments.filter(status__in=['in_transit', 'sorting_center', 'out_for_delivery']).count()
    failed_shipments = shipments.filter(status__in=['failed_delivery', 'returned']).count()

    # Financial stats
    total_revenue = Invoice.objects.filter(status='paid').aggregate(total=Sum('amount_ttc'))['total'] or 0
    # Calculate pending payments as sum of (amount_ttc - amount_paid) for unpaid/partially paid invoices
    unpaid_invoices = Invoice.objects.filter(status__in=['issued', 'partially_paid', 'overdue'])
    pending_payments = sum(invoice.balance_due for invoice in unpaid_invoices if invoice.balance_due > 0)

    # Client stats
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()

    # Driver stats
    total_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(is_active=True).count()

    # Incident stats
    total_incidents = Incident.objects.count()
    open_incidents = Incident.objects.filter(status__in=['reported', 'investigating']).count()

    return {
        'total_shipments': total_shipments,
        'delivered_shipments': delivered_shipments,
        'in_transit_shipments': in_transit_shipments,
        'failed_shipments': failed_shipments,
        'success_rate': (delivered_shipments / total_shipments * 100) if total_shipments > 0 else 0,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'total_drivers': total_drivers,
        'active_drivers': active_drivers,
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
    }

# ==================== COMMERCIAL ANALYTICS ====================

def commercial_analytics(request):
    """MG-01 to MG-04: Commercial analytics"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    # Date range for analytics (last 12 months by default)
    end_date = timezone.now().date()
    # Calculate start date: 12 months ago, first day of that month
    if end_date.month >= 12:
        start_date = date(end_date.year - 1, 1, 1)
    else:
        start_date = date(end_date.year - 1, end_date.month + 1, 1)

    # MG-01 & MG-02: Shipments and revenue evolution
    monthly_data = []
    current_date = start_date
    for i in range(12):
        if current_date > end_date:
            break
        month_date = current_date

        month_shipments = Shipment.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()

        month_revenue = Shipment.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate growth percentage
        growth_pct = None
        if len(monthly_data) > 0:
            prev_revenue = monthly_data[-1]['revenue']
            if prev_revenue > 0:
                growth_pct = ((float(month_revenue) - prev_revenue) / prev_revenue) * 100
        
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'shipments': month_shipments,
            'revenue': float(month_revenue),
            'growth_pct': growth_pct
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)

    # MG-03: Top clients by shipment volume and value
    top_clients_volume = Client.objects.annotate(
        shipment_count=Count('shipments')
    ).order_by('-shipment_count')[:10]

    top_clients_value = Client.objects.annotate(
        total_value=Sum('invoices__amount_ttc')
    ).order_by('-total_value')[:10]

    # MG-04: Top destinations
    top_destinations = Destination.objects.annotate(
        shipment_count=Count('shipment'),
        revenue=Sum('shipment__amount')
    ).order_by('-shipment_count')[:10]

    context = {
        'monthly_data': monthly_data,
        'top_clients_volume': top_clients_volume,
        'top_clients_value': top_clients_value,
        'top_destinations': top_destinations,
        'date_range': {'start': start_date, 'end': end_date}
    }

    return render(request, 'manager/commercial_analytics.html', context)

# ==================== OPERATIONAL ANALYTICS ====================

def operational_analytics(request):
    """MG-05 to MG-09: Operational analytics"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    # Date range for analytics (last 12 months by default)
    end_date = timezone.now().date()
    # Calculate start date: 12 months ago, first day of that month
    if end_date.month >= 12:
        start_date = date(end_date.year - 1, 1, 1)
    else:
        start_date = date(end_date.year - 1, end_date.month + 1, 1)

    # MG-05: Tours evolution
    monthly_tours = []
    current_date = start_date
    for i in range(12):
        if current_date > end_date:
            break
        month_date = current_date

        tours_count = DeliveryTour.objects.filter(
            date__year=month_date.year,
            date__month=month_date.month
        ).count()

        completed_tours = DeliveryTour.objects.filter(
            date__year=month_date.year,
            date__month=month_date.month,
            status='completed'
        ).count()

        monthly_tours.append({
            'month': month_date.strftime('%b %Y'),
            'total_tours': tours_count,
            'completed_tours': completed_tours,
            'completion_rate': (completed_tours / tours_count * 100) if tours_count > 0 else 0
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)

    # MG-06: Delivery success rate
    total_shipments = Shipment.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()

    successful_deliveries = Shipment.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='delivered'
    ).count()

    delivery_success_rate = (successful_deliveries / total_shipments * 100) if total_shipments > 0 else 0

    # MG-07: Top drivers performance
    top_drivers_qs = Driver.objects.annotate(
        tours_completed=Count('tours', filter=Q(tours__status='completed')),
        total_shipments=Count('tours__tour_shipments', distinct=True)
    ).filter(total_shipments__gt=0).order_by('-total_shipments')[:10]
    
    # Convert to list and calculate success rate
    top_drivers = list(top_drivers_qs)
    for driver in top_drivers:
        # Calculate delivered shipments for each driver
        delivered_count = 0
        for tour in driver.tours.all():
            for tour_shipment in tour.tour_shipments.all():
                if tour_shipment.shipment.status == 'delivered':
                    delivered_count += 1
        driver.shipments_delivered = delivered_count
        driver.success_rate = (driver.shipments_delivered / driver.total_shipments * 100) if driver.total_shipments > 0 else 0


    # MG-08: Incident-prone zones
    incident_zones = Destination.objects.annotate(
        incident_count=Count('shipment__incidents')
    ).filter(incident_count__gt=0).order_by('-incident_count')[:10]

    # MG-09: Peak activity periods (by hour of day)
    hourly_activity = []
    for hour in range(24):
        shipment_count = Shipment.objects.filter(
            created_at__hour=hour,
            created_at__date__range=[start_date, end_date]
        ).count()

        hourly_activity.append({
            'hour': hour,
            'count': shipment_count
        })

    context = {
        'monthly_tours': monthly_tours,
        'delivery_success_rate': delivery_success_rate,
        'total_shipments': total_shipments,
        'successful_deliveries': successful_deliveries,
        'top_drivers': top_drivers,
        'incident_zones': incident_zones,
        'hourly_activity': hourly_activity,
        'date_range': {'start': start_date, 'end': end_date}
    }

    return render(request, 'manager/operational_analytics.html', context)

# ==================== MANAGEMENT VIEWS ====================

def shipment_management(request):
    """View and manage all shipments"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    shipments = Shipment.objects.select_related('client', 'destination', 'service_type').all()

    # Filters
    status = request.GET.get('status')
    client_id = request.GET.get('client')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status:
        shipments = shipments.filter(status=status)
    if client_id:
        shipments = shipments.filter(client_id=client_id)
    if date_from:
        shipments = shipments.filter(created_at__date__gte=date_from)
    if date_to:
        shipments = shipments.filter(created_at__date__lte=date_to)

    shipments = shipments.order_by('-created_at')

    # Pagination
    paginator = Paginator(shipments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter options
    clients = Client.objects.all()
    statuses = Shipment.STATUS_CHOICES

    return render(request, 'manager/shipment_management.html', {
        'page_obj': page_obj,
        'clients': clients,
        'statuses': statuses,
        'filters': {
            'status': status,
            'client': client_id,
            'date_from': date_from,
            'date_to': date_to
        }
    })

def client_management(request):
    """View and manage all clients"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    # Search functionality
    search_query = request.GET.get('search', '')
    clients = Client.objects.annotate(
        shipment_count=Count('shipments'),
        total_spent=Sum('invoices__amount_ttc')
    )

    # Filter by search query
    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(client_id__icontains=search_query)
        )

    clients = clients.order_by('-created_at')

    # Pagination
    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/client_management.html', {
        'page_obj': page_obj,
        'object_list': page_obj.object_list,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    })

def driver_management(request):
    """View and manage all drivers"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    drivers = Driver.objects.annotate(
        tour_count=Count('tours'),
        total_shipments=Count('tours__tour_shipments', distinct=True)
    ).order_by('-hire_date')

    # Calculate delivered shipments and success rates
    for driver in drivers:
        delivered_count = 0
        total_count = 0
        for tour in driver.tours.all():
            for tour_shipment in tour.tour_shipments.all():
                total_count += 1
                if tour_shipment.shipment.status == 'delivered':
                    delivered_count += 1
        driver.delivery_count = delivered_count
        driver.total_shipments = total_count
        driver.success_rate = (driver.delivery_count / driver.total_shipments * 100) if driver.total_shipments > 0 else 0

    # Pagination
    paginator = Paginator(drivers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/driver_management.html', {
        'page_obj': page_obj
    })

def incident_management(request):
    """View and manage all incidents"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    incidents = Incident.objects.select_related('client', 'shipment').all()

    # Filter by status
    status = request.GET.get('status')
    if status:
        incidents = incidents.filter(status=status)

    incidents = incidents.order_by('-reported_date')

    # Pagination
    paginator = Paginator(incidents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/incident_management.html', {
        'page_obj': page_obj,
        'status_filter': status,
        'status_choices': Incident.STATUS_CHOICES
    })

def tour_management(request):
    """View and manage all delivery tours"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    tours = DeliveryTour.objects.select_related('driver', 'vehicle').annotate(
        total_shipments=Count('tour_shipments')
    ).all()

    # Filters
    status = request.GET.get('status')
    date = request.GET.get('date')

    if status:
        tours = tours.filter(status=status)
    if date:
        tours = tours.filter(date=date)

    tours = tours.order_by('-date', '-created_at')

    # Pagination
    paginator = Paginator(tours, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/tour_management.html', {
        'page_obj': page_obj,
        'status_choices': DeliveryTour.STATUS_CHOICES,
        'filters': {'status': status, 'date': date}
    })

# ==================== REPORTS ====================

def system_reports(request):
    """Generate various system reports"""
    if not request.user.is_authenticated or request.user.role != 'manager':
        return redirect('/auth/manager/login/')

    manager = request.user

    report_type = request.GET.get('type', 'summary')

    if report_type == 'clients':
        # Client report
        clients = Client.objects.annotate(
            shipment_count=Count('shipments'),
            total_spent=Sum('invoices__amount_ttc'),
            last_shipment_date=Max('shipments__created_at')
        ).order_by('-total_spent')

        context = {
            'report_title': 'Client Performance Report',
            'clients': clients,
            'report_type': report_type
        }

    elif report_type == 'drivers':
        # Driver performance report
        drivers = Driver.objects.annotate(
            tours_completed=Count('tours', filter=Q(tours__status='completed')),
            total_deliveries=Count('tours__tour_shipments')
        ).order_by('-total_deliveries')

        context = {
            'report_title': 'Driver Performance Report',
            'drivers': drivers,
            'report_type': report_type
        }

    else:
        # Summary report
        stats = get_system_stats()
        context = {
            'report_title': 'System Summary Report',
            'stats': stats,
            'report_type': report_type
        }

    return render(request, 'manager/system_reports.html', context)