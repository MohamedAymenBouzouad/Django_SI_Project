from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from common.models import Client, Shipment, Invoice, Payment, Claim, TrackingEvent
from authentication.models import User

def get_client_from_request(request):
    """Helper function to get client from authenticated user"""
    if not request.user.is_authenticated:
        return None

    try:
        return Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        return None

# ==================== CLIENT DASHBOARD ====================

def client_dashboard(request):
    """CL-01: View own profile & balance, CL-02: Track shipments, CL-04: View invoices"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    # Get dashboard data
    recent_shipments = Shipment.objects.filter(client=client).select_related('destination').order_by('-created_at')[:10]
    active_shipments = Shipment.objects.filter(
        client=client,
        status__in=['in_transit', 'at_sorting_center', 'out_for_delivery']
    )
    pending_invoices = Invoice.objects.filter(client=client, status__in=['issued', 'partially_paid', 'overdue'])

    # Calculate statistics
    total_shipments = Shipment.objects.filter(client=client).count()
    delivered_shipments = Shipment.objects.filter(client=client, status='delivered').count()
    from django.db.models import Sum
    total_spent = Payment.objects.filter(invoice__client=client).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'client': client,
        'recent_shipments': recent_shipments,
        'active_shipments': active_shipments,
        'pending_invoices': pending_invoices,
        'total_shipments': total_shipments,
        'delivered_shipments': delivered_shipments,
        'in_transit_shipments': total_shipments - delivered_shipments,
        'total_spent': total_spent,
        'pending_amount': sum(invoice.balance_due for invoice in pending_invoices)
    }

    return render(request, 'client/dashboard.html', context)

# ==================== SHIPMENT TRACKING ====================

def shipment_list(request):
    """CL-03: View shipment history"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    shipments = Shipment.objects.filter(client=client).select_related('destination').order_by('-created_at')

    # Pagination
    paginator = Paginator(shipments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'client/shipment_list.html', {
        'client': client,
        'page_obj': page_obj
    })

def shipment_detail(request, shipment_id):
    """CL-02: Track shipments (real-time)"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    shipment = get_object_or_404(Shipment.objects.select_related('destination', 'client'), id=shipment_id, client=client)
    tracking_history = TrackingEvent.objects.filter(shipment=shipment).order_by('-timestamp')

    return render(request, 'client/shipment_detail.html', {
        'client': client,
        'shipment': shipment,
        'tracking_history': tracking_history
    })

def track_shipment(request):
    """CL-02: Track shipment by number"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')

        try:
            shipment = Shipment.objects.get(
                shipment_number=tracking_number,
                client=client
            )
            return redirect('client:shipment_detail', shipment_id=shipment.id)

        except Shipment.DoesNotExist:
            messages.error(request, "Shipment not found or doesn't belong to your account.")

    return render(request, 'client/track_shipment.html', {'client': client})

# ==================== INVOICE MANAGEMENT ====================

def invoice_list(request):
    """CL-04: View payment history"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    invoices = Invoice.objects.filter(client=client).order_by('-issue_date')

    # Pagination
    paginator = Paginator(invoices, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'client/invoice_list.html', {
        'client': client,
        'page_obj': page_obj
    })

def invoice_detail(request, invoice_id):
    """CL-04: Download invoice PDF (view details)"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    invoice = get_object_or_404(Invoice, id=invoice_id, client=client)
    payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date')

    return render(request, 'client/invoice_detail.html', {
        'client': client,
        'invoice': invoice,
        'payments': payments
    })

# ==================== CLAIMS MANAGEMENT ====================

def submit_claim(request):
    """CL-06: Submit claim"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    if request.method == 'POST':
        subject = request.POST.get('title') or request.POST.get('subject', '')
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        if category:
            description = f"[Category: {category}]\n\n{description}"
        shipment_id = request.POST.get('shipment_id')
        priority = request.POST.get('priority', 'medium')

        claim = Claim.objects.create(
            subject=subject,
            description=description,
            priority=priority,
            client=client,
            created_by=request.user,
            shipment_id=shipment_id if shipment_id else None
        )

        messages.success(request, "Claim submitted successfully!")
        return redirect('client:claim_detail', claim_id=claim.id)

    # GET request
    shipments = Shipment.objects.filter(client=client).select_related('destination').order_by('-created_at')[:50]
    return render(request, 'client/submit_claim.html', {
        'client': client,
        'shipments': shipments
    })

def claim_list(request):
    """CL-07: Track claim status"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    claims = Claim.objects.filter(client=client).select_related('shipment', 'shipment__destination', 'shipment__client').order_by('-filed_date')

    # Pagination
    paginator = Paginator(claims, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'client/claim_list.html', {
        'client': client,
        'page_obj': page_obj
    })

def claim_detail(request, claim_id):
    """CL-07: Track claim status (detailed view)"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    claim = get_object_or_404(
        Claim.objects.select_related('shipment', 'shipment__destination', 'shipment__client'),
        id=claim_id, client=client
    )

    return render(request, 'client/claim_detail.html', {
        'client': client,
        'claim': claim
    })

# ==================== PROFILE MANAGEMENT ====================

def client_profile(request):
    """CL-01: View own profile & balance"""
    if not request.user.is_authenticated or request.user.role != 'client':
        return redirect('/auth/client/login/')

    try:
        client = Client.objects.get(auth_user=request.user)
    except Client.DoesNotExist:
        logout(request)
        return redirect('/auth/client/login/?error=Profile%20not%20found.%20Please%20contact%20support.')

    if request.method == 'POST':
        # Handle profile updates
        client.phone = request.POST.get('phone', client.phone)
        client.address = request.POST.get('address', client.address)
        client.city = request.POST.get('city', client.city)
        client.postal_code = request.POST.get('postal_code', client.postal_code)
        client.country = request.POST.get('country', client.country)
        client.save()

        messages.success(request, "Profile updated successfully!")

    return render(request, 'client/profile.html', {'client': client})