from django.db import models
from common.models import Client, Driver, Vehicle, Destination, ServiceType, Shipment, Invoice, Incident, Claim, Favorite

# Agent app uses common models directly
# This file contains any agent-specific extensions if needed

class AgentProfile(models.Model):
    """
    Agent-specific profile data
    """
    username = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=50, default='operations')
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'agent'