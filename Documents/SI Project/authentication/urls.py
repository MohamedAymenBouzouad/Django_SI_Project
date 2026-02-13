from django.urls import path
from . import views

urlpatterns = [
    # Login views
    path('agent/login/', views.agent_login, name='agent_login'),
    path('manager/login/', views.manager_login, name='manager_login'),
    path('client/login/', views.client_login, name='client_login'),
    path('driver/login/', views.driver_login, name='driver_login'),

    path('logout/', views.logout_view, name='logout'),
]