from django.db import models

class Route(models.Model):
    # Basic information
    number = models.CharField(max_length=10, unique=True) # e.g., "101", "Xpress"
    name = models.CharField(max_length=100) # e.g., "Downtown to Airport Express"
    description = models.TextField(blank=True, null=True)

    # Operational details
    origin = models.CharField(max_length=100) # Starting point
    destination = models.CharField(max_length=100) # Ending point
    total_distance = models.DecimalField(max_digits=6, decimal_places=2, help_text="Distance in kilometers") # e.g., 22.50 km
    # NEW FIELD: Add this. Duration of the trip in hours (e.g., 1.5 for 1 hour 30 minutes)
    duration = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.0,
        help_text="Duration of the trip in hours (e.g., 1.5 for 1 hour 30 minutes)"
    )

    # NEW FIELDS: Operational timings
    turnaround_time = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.33, 
        help_text="Turnaround time at terminal in hours (e.g., 0.33 for 20 minutes)"
    )
    buffer_time = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.16, 
        help_text="Buffer time for delays in hours (e.g., 0.16 for 10 minutes)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number}: {self.origin} to {self.destination}"
    
    # NEW METHOD: Calculate trips per day
    def calculate_trips_per_day(self, operational_hours=15):
        """
        Calculate how many round trips a bus can make on this route in a day.
        operational_hours: Default is 15 (6 AM to 9 PM). Can be overridden.
        """
        # Calculate total time for one round trip: (A->B + B->A) + turnaround + buffer
        total_time_per_trip = (self.duration * 2) + self.turnaround_time + self.buffer_time
        # Calculate how many trips fit into the operational window
        trips = operational_hours / total_time_per_trip
        # Return the result, rounded down to the nearest whole number
        return int(trips)


class Stop(models.Model):
    # Link this stop to a specific route
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    # Details about the stop itself
    name = models.CharField(max_length=100) # e.g., "Central Library", "Maple St & 5th Ave"
    sequence = models.PositiveIntegerField() # Order of the stop on the route (1, 2, 3...)
    distance_from_origin = models.DecimalField(max_digits=6, decimal_places=2, help_text="Distance from route start in km")

    # Meta class defines database constraints and ordering
    class Meta:
        # Ensure the stop order is unique for each route
        unique_together = ['route', 'sequence']
        # Ensure the stop name is unique within a route (optional, but good practice)
        unique_together = ['route', 'name']
        # Order stops by their sequence number by default
        ordering = ['sequence']

    def __str__(self):
        return f"{self.sequence}. {self.name} (Route {self.route.number})"