from django.db import models

class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used_hrs = models.DecimalField(max_digits=5, decimal_places=2)

    route_distance_miles = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    route_duration_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    route_geojson = models.JSONField(null=True, blank=True)

    daily_logs = models.JSONField(null=True, blank=True)
    stops = models.JSONField(null=True, blank=True)     

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip from {self.pickup_location} to {self.dropoff_location}"