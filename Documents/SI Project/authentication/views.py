from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from .models import User
from .forms import ClientSignupForm, DriverSignupForm
from common.models import Client, Driver

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

    return render(request, 'authentication/agent_login.html')


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

    return render(request, 'authentication/manager_login.html')


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
    return render(request, 'authentication/client_login.html', {'error': error_message})


def driver_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.role == 'driver':
                from django.contrib.auth import login
                login(request, user)
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                return redirect('/driver/dashboard/')
            else:
                return render(request, 'authentication/driver_login.html', {
                    'error': 'Invalid credentials or not a driver'
                })
        except User.DoesNotExist:
            return render(request, 'authentication/driver_login.html', {
                'error': 'Invalid credentials or not a driver'
            })

    return render(request, 'authentication/driver_login.html')


def logout_view(request):
    """Log out and redirect to home."""
    logout(request)
    return redirect('/')


