from django.db import models
from common.models import Client as CommonClient

# The client app uses the common Client model directly
# This allows the client app to work independently with the common models

class ClientProfile(CommonClient):
    """
    Extended client profile for the client app
    This inherits from the common Client model and adds client-specific functionality
    """
    # Additional client-specific fields can be added here if needed
    # For now, we use the common Client model directly

    class Meta:
        proxy = True  # This makes it a proxy model that doesn't create a new table
        app_label = 'client'

    def get_active_shipments(self):
        """Get shipments that are currently in transit"""
        from common.models import Shipment
        return Shipment.objects.filter(
            client=self,
            status__in=['in_transit', 'sorting_center', 'out_for_delivery']
        )

    def get_shipment_history(self, limit=50):
        """Get shipment history"""
        from common.models import Shipment
        return Shipment.objects.filter(client=self).order_by('-created_at')[:limit]

    def get_unpaid_invoices(self):
        """Get unpaid invoices"""
        from common.models import Invoice
        return Invoice.objects.filter(
            client=self,
            status__in=['sent', 'overdue']
        ).order_by('due_date')

    def get_recent_claims(self, limit=10):
        """Get recent claims"""
        from common.models import Claim
        return Claim.objects.filter(client=self).order_by('-submitted_date')[:limit]