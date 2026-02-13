"""
URL configuration for FinalProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from authentication import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),

    # Authentication URLs (login and signup)
    path('auth/', include('authentication.urls')),

    # Legacy login URLs for backward compatibility
    path('login/agent/', auth_views.agent_login, name='agent_login'),
    path('login/manager/', auth_views.manager_login, name='manager_login'),
    path('login/client/', auth_views.client_login, name='client_login'),
    path('login/driver/', auth_views.driver_login, name='driver_login'),

    # Application URLs
    path('agent/', include('agent.urls')),
    path('manager/', include('manager.urls')),
    path('client/', include('client.urls')),
    path('driver/', include('driver.urls')),
]
