from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from common.models import Client, Driver, Manager, Agent

class User(AbstractUser):
    """
    Custom user model that connects to common app models
    Uses simple password checking instead of Django auth
    """
    ROLE_CHOICES = [
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('client', 'Client'),
        ('driver', 'Driver'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    # Store password in plain text for simple checking (not recommended for production)
    simple_password = models.CharField(max_length=128, blank=True)

    # Links to common app models
    client_profile = models.OneToOneField(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')
    driver_profile = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')
    manager_profile = models.OneToOneField(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')
    agent_profile = models.OneToOneField(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def set_password(self, raw_password):
        """Override to store simple password"""
        self.simple_password = raw_password
        super().set_password(raw_password)

    def check_password(self, raw_password):
        """Check password - try both simple and Django's hashed password"""
        # First try simple password (for app logins)
        if self.simple_password and self.simple_password == raw_password:
            return True
        # Then try Django's standard password checking (for admin)
        return super().check_password(raw_password)

    def get_dashboard_url(self):
        """Return the appropriate dashboard URL based on role"""
        role_urls = {
            'agent': '/agent/dashboard/',
            'manager': '/manager/dashboard/',
            'client': '/client/dashboard/',
            'driver': '/driver/dashboard/',
        }
        return role_urls.get(self.role, '/')

    def can_access_app(self, app_name):
        """Check if user can access a specific app"""
        role_app_mapping = {
            'agent': ['agent'],
            'manager': ['manager'],
            'client': ['client'],
            'driver': ['driver'],
        }
        allowed_apps = role_app_mapping.get(self.role, [])
        return app_name in allowed_apps