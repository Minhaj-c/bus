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

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number}: {self.origin} to {self.destination}"

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