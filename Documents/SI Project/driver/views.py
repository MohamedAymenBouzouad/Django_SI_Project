from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from common.models import Driver, DeliveryTour, Shipment, TrackingEvent, Incident
from authentication.models import User

def get_driver_from_request(request):
    """Helper function to get driver from authenticated user"""
    if not request.user.is_authenticated:
        return None

    try:
        return Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return None

# ==================== DRIVER DASHBOARD ====================

def driver_dashboard(request):
    """DR-01: View assigned tours"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    # Get active tours for this driver
    active_tours = DeliveryTour.objects.filter(
        driver=driver,
        status__in=['planned', 'in_progress']
    ).order_by('planned_date')

    # Get today's shipments
    today = timezone.now().date()
    todays_shipments = Shipment.objects.filter(
        assigned_tour__driver=driver,
        assigned_tour__planned_date=today
    )

    # Performance metrics
    delivered_count = todays_shipments.filter(status='delivered').count()
    total_count = todays_shipments.count()
    completion_rate = (delivered_count / total_count * 100) if total_count > 0 else 0

    context = {
        'driver': driver,
        'active_tours': active_tours,
        'todays_shipments': todays_shipments,
        'pending_deliveries': todays_shipments.filter(status='out_for_delivery').count(),
        'performance': {
            'delivered': delivered_count,
            'total': total_count,
            'completion_rate': completion_rate
        },
        'current_tour': DeliveryTour.objects.filter(
            driver=driver,
            status='in_progress'
        ).first()
    }

    return render(request, 'driver/dashboard.html', context)

# ==================== TOUR MANAGEMENT ====================

def tour_list(request):
    """DR-01: View assigned tours (all tours for driver)"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    tours = DeliveryTour.objects.filter(driver=driver).order_by('-planned_date')

    return render(request, 'driver/tour_list.html', {
        'driver': driver,
        'tours': tours
    })

def tour_detail(request, tour_id):
    """DR-02: View shipments in tour"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    tour = get_object_or_404(DeliveryTour, id=tour_id, driver=driver)
    shipments = tour.shipments.all()

    return render(request, 'driver/tour_detail.html', {
        'driver': driver,
        'tour': tour,
        'shipments': shipments
    })

def start_tour(request, tour_id):
    """DR-03: Start tour"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    tour = get_object_or_404(DeliveryTour, id=tour_id, driver=driver)

    if tour.status != 'planned':
        messages.error(request, "Tour cannot be started.")
        return redirect('driver:tour_detail', tour_id=tour_id)

    tour.status = 'in_progress'
    tour.actual_start_time = timezone.now()
    tour.save()

    # Update all shipments to 'in_transit'
    for shipment in tour.shipments.all():
        shipment.status = 'in_transit'
        shipment.save()

        TrackingEvent.objects.create(
            shipment=shipment,
            status='in_transit',
            tour=tour,
            notes='Tour started - shipment in transit'
        )

    messages.success(request, f"Tour {tour.tour_number} started successfully!")
    return redirect('driver:tour_detail', tour_id=tour_id)

def complete_tour(request, tour_id):
    """DR-07: Close tour"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    tour = get_object_or_404(DeliveryTour, id=tour_id, driver=driver)

    if tour.status != 'in_progress':
        messages.error(request, "Tour is not in progress.")
        return redirect('driver:tour_detail', tour_id=tour_id)

    tour.status = 'completed'
    tour.actual_end_time = timezone.now()
    tour.save()

    messages.success(request, f"Tour {tour.tour_number} completed successfully!")
    return redirect('driver:tour_list')

# ==================== SHIPMENT STATUS UPDATES ====================

def update_shipment_status(request, shipment_id):
    """DR-04: Update shipment status (delivered/failed)"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return JsonResponse({'error': 'Driver not found'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    shipment = get_object_or_404(Shipment, id=shipment_id, assigned_tour__driver=driver)

    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')

    if new_status not in ['delivered', 'failed_delivery']:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    # Update shipment status
    shipment.status = new_status
    if new_status == 'delivered':
        shipment.actual_delivery_date = timezone.now()
    shipment.save()

    # Create tracking entry
    TrackingEvent.objects.create(
        shipment=shipment,
        status=new_status,
        tour=shipment.assigned_tour,
        notes=notes
    )

    return JsonResponse({
        'success': True,
        'message': f'Shipment {shipment.tracking_number} marked as {new_status}'
    })

def add_tracking_event(request, shipment_id):
    """DR-05: Add tracking event"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    shipment = get_object_or_404(Shipment, id=shipment_id, assigned_tour__driver=driver)

    if request.method == 'POST':
        status = request.POST.get('status')
        location = request.POST.get('location', '')
        notes = request.POST.get('notes', '')

        TrackingEvent.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            tour=shipment.assigned_tour,
            notes=notes
        )

        messages.success(request, 'Tracking event added successfully!')
        return redirect('driver:tour_detail', tour_id=shipment.assigned_tour.id)

    return render(request, 'driver/add_tracking.html', {
        'driver': driver,
        'shipment': shipment
    })

# ==================== INCIDENT REPORTING ====================

def report_incident(request, shipment_id=None):
    """DR-06: Report incident"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return redirect('/auth/driver/login/')

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return redirect('/auth/driver/login/')

    if request.method == 'POST':
        incident_type = request.POST.get('type')
        description = request.POST.get('description')
        location = request.POST.get('location', '')

        # Validate incident type
        valid_types = [choice[0] for choice in Incident.TYPE_CHOICES]
        if incident_type not in valid_types:
            messages.error(request, "Invalid incident type.")
            return redirect('driver:dashboard')

        incident = Incident.objects.create(
            type=incident_type,
            title=f"Incident reported by {driver.user.username}",
            description=description,
            location=location,
            shipment_id=shipment_id if shipment_id else None,
            # Associate with current tour if no specific shipment
            tour=DeliveryTour.objects.filter(
                driver=driver,
                status='in_progress'
            ).first() if not shipment_id else None,
        )

        messages.success(request, 'Incident reported successfully!')
        return redirect('driver:dashboard')

    # GET request - show form
    context = {
        'incident_types': Incident.TYPE_CHOICES,
        'driver': driver,
    }

    if shipment_id:
        shipment = get_object_or_404(Shipment, id=shipment_id, assigned_tour__driver=driver)
        context['shipment'] = shipment

    return render(request, 'driver/report_incident.html', context)

# ==================== LOCATION TRACKING ====================

def update_location(request):
    """Update driver's current location"""
    if not request.user.is_authenticated or request.user.role != 'driver':
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        driver = Driver.objects.get(auth_user=request.user)
    except Driver.DoesNotExist:
        return JsonResponse({'error': 'Driver not found'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))
        accuracy = float(request.POST.get('accuracy', 0))

        driver.current_latitude = latitude
        driver.current_longitude = longitude
        driver.location_accuracy = accuracy
        driver.last_location_timestamp = timezone.now()
        driver.save(update_fields=[
            'current_latitude', 'current_longitude',
            'location_accuracy', 'last_location_timestamp'
        ])

        return JsonResponse({
            'success': True,
            'message': 'Location updated successfully'
        })

    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)