from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from authentication.models import User

def agent_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check against authentication User model
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.role == 'agent':
                # Use Django's login for admin compatibility
                from django.contrib.auth import login
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                return redirect('/agent/dashboard/')
            else:
                return render(request, 'authentication/agent_login.html', {
                    'error': 'Invalid credentials or not an agent'
                })
        except User.DoesNotExist:
            return render(request, 'authentication/agent_login.html', {
                'error': 'Invalid credentials or not an agent'
            })

    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    return render(request, 'authentication/agent_login.html', {'csrf_token': csrf_token})


def manager_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.role == 'manager':
                from django.contrib.auth import login
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                return redirect('/manager/dashboard/')
            else:
                return render(request, 'authentication/manager_login.html', {
                    'error': 'Invalid credentials or not a manager'
                })
        except User.DoesNotExist:
            return render(request, 'authentication/manager_login.html', {
                'error': 'Invalid credentials or not a manager'
            })

    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    return render(request, 'authentication/manager_login.html', {'csrf_token': csrf_token})


def client_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.role == 'client':
                from django.contrib.auth import login
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                return redirect('/client/dashboard/')
            else:
                return render(request, 'authentication/client_login.html', {
                    'error': 'Invalid credentials.'
                })
        except User.DoesNotExist:
            return render(request, 'authentication/client_login.html', {
                'error': 'Invalid credentials.'
            })

    error_message = request.GET.get('error')
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    return render(request, 'authentication/client_login.html', {'error': error_message, 'csrf_token': csrf_token})


def driver_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.role == 'driver':
                # Check if driver profile is assigned
                if not user.driver_profile:
                    return render(request, 'authentication/driver_login.html', {
                        'error': 'Driver profile not assigned to this user'
                    })
                from django.contrib.auth import login
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                request.session['driver_id'] = user.driver_profile.id
                return redirect('/driver/dashboard/')
            else:
                return render(request, 'authentication/driver_login.html', {
                    'error': 'Invalid credentials or not a driver'
                })
        except User.DoesNotExist:
            return render(request, 'authentication/driver_login.html', {
                'error': 'Invalid credentials or not a driver'
            })

    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    return render(request, 'authentication/driver_login.html', {'csrf_token': csrf_token})


def logout_view(request):
    """Log out and redirect to home."""
    logout(request)
    return redirect('/')


