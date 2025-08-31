from django.db import models
from django.conf import settings # To reference the CustomUser model
from routes.models import Route # To reference the Route model

class Bus(models.Model):
    number_plate = models.CharField(max_length=15, unique=True) # e.g., "ABC-1234"
    capacity = models.PositiveIntegerField(default=40) # Total number of seats
    mileage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, help_text="Mileage in km/liter") 
    SERVICE_TYPES = (
        ('all_stop', 'All Stop Service'),
        ('limited_stop', 'Limited Stop Service'),
        ('express', 'Express Service'), # You can add more types later
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='all_stop')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.number_plate} (Seats: {self.capacity})"

class Schedule(models.Model):
    # The core relationship: Which route is this bus running?
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    # Which physical bus is assigned?
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    # Which driver is assigned? Link only to users with the 'driver' role.
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'driver'}, # CRITICAL: Only drivers can be assigned
        related_name='schedules'
    )

    # When does this trip happen?
    date = models.DateField()
    departure_time = models.TimeField() # Start time from the origin
    arrival_time = models.TimeField() # Approximate arrival at destination

    # SEAT AVAILABILITY - THE CORE OF YOUR NEW FEATURE
    total_seats = models.PositiveIntegerField() # Should equal bus.capacity, but stored for record-keeping
    available_seats = models.PositiveIntegerField() # This number decreases with each booking

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent double-booking a bus or driver on the same date and time
        unique_together = ['bus', 'date', 'departure_time']
        unique_together = ['driver', 'date', 'departure_time']
        # Order schedules by date and time by default
        ordering = ['date', 'departure_time']

    def __str__(self):
        return f"{self.route.number} - {self.date} {self.departure_time} ({self.bus.number_plate})"

    # A helpful method to check if seats are available
    def is_seat_available(self):
        return self.available_seats > 0

    # A method to "book" a seat (we will use this later)
    def book_seat(self):
        if self.is_seat_available():
            self.available_seats -= 1
            self.save()
            return True
        return False