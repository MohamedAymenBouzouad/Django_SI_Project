from django.db import models
from common.models import Driver as CommonDriver

# The driver app uses the common Driver model directly
# This allows the driver app to work independently with the common models

class DriverProfile(CommonDriver):
    """
    Extended driver profile for the driver app
    This inherits from the common Driver model and adds driver-specific functionality
    """
    # Additional driver-specific fields can be added here if needed
    # For now, we use the common Driver model directly

    class Meta:
        proxy = True  # This makes it a proxy model that doesn't create a new table
        app_label = 'driver'

    def get_today_performance(self):
        """Get today's delivery performance"""
        from django.utils import timezone
        from common.models import Shipment

        today = timezone.now().date()
        todays_shipments = Shipment.objects.filter(
            assigned_tour__driver=self,
            assigned_tour__planned_date=today
        )

        delivered = todays_shipments.filter(status='delivered').count()
        total = todays_shipments.count()

        return {
            'delivered': delivered,
            'total': total,
            'completion_rate': (delivered / total * 100) if total > 0 else 0
        }

    def get_current_tour(self):
        """Get the driver's current active tour"""
        from common.models import DeliveryTour
        from django.utils import timezone

        return DeliveryTour.objects.filter(
            driver=self,
            status='in_progress'
        ).first()

    def update_location(self, latitude, longitude, accuracy=0):
        """Update driver's current location"""
        from django.utils import timezone

        self.current_latitude = latitude
        self.current_longitude = longitude
        self.location_accuracy = accuracy
        self.last_location_timestamp = timezone.now()
        self.save(update_fields=[
            'current_latitude', 'current_longitude',
            'location_accuracy', 'last_location_timestamp'
        ])
        return True