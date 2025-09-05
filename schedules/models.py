from django.db import models
from django.conf import settings
from routes.models import Route
from django.utils import timezone

class Bus(models.Model):
    number_plate = models.CharField(max_length=15, unique=True)
    capacity = models.PositiveIntegerField(default=40)
    mileage = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, help_text="Mileage in km/liter")
    
    SERVICE_TYPES = (
        ('all_stop', 'All Stop Service'),
        ('limited_stop', 'Limited Stop Service'),
        ('express', 'Express Service'),
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='all_stop')
    is_active = models.BooleanField(default=True)
    
    # Location tracking fields
    current_latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        help_text="Current GPS latitude"
    )
    current_longitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True,
        help_text="Current GPS longitude" 
    )
    last_location_update = models.DateTimeField(
        null=True, blank=True,
        help_text="When location was last updated"
    )
    is_running = models.BooleanField(
        default=False,
        help_text="Is bus currently on route"
    )
    current_route = models.ForeignKey(
        Route, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Route currently being served"
    )

    def __str__(self):
        return f"{self.number_plate} (Seats: {self.capacity})"
    
    def save(self, *args, **kwargs):
        """Override save to auto-update last_location_update when location changes"""
        # Check if this is an update (not a new creation)
        if self.pk:
            # Get the original object from database
            try:
                original = Bus.objects.get(pk=self.pk)
                # Check if location fields have changed
                if (original.current_latitude != self.current_latitude or 
                    original.current_longitude != self.current_longitude):
                    self.last_location_update = timezone.now()
            except Bus.DoesNotExist:
                pass
        else:
            # For new objects, set last_location_update if location is provided
            if self.current_latitude and self.current_longitude:
                self.last_location_update = timezone.now()
        
        super().save(*args, **kwargs)
    
    def update_location(self, latitude, longitude):
        """Update bus location with timestamp"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_location_update = timezone.now()
        self.save(update_fields=['current_latitude', 'current_longitude', 'last_location_update'])


class Schedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'driver'},
        related_name='schedules'
    )
    
    date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ['bus', 'date', 'departure_time'],
            ['driver', 'date', 'departure_time']
        ]
        ordering = ['date', 'departure_time']

    def __str__(self):
        return f"{self.route.number} - {self.date} {self.departure_time} ({self.bus.number_plate})"

    def is_seat_available(self):
        return self.available_seats > 0

    def book_seat(self):
        if self.is_seat_available():
            self.available_seats -= 1
            self.save()
            return True
        return False


class BusSchedule(models.Model):
    """Operational planning - which bus runs which route when"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_schedules')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='bus_schedules')
    date = models.DateField(help_text="Date of the assignment")
    start_time = models.TimeField(help_text="When the bus starts this route")
    end_time = models.TimeField(help_text="When the bus finishes this route")
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Bus Assignment'
        verbose_name_plural = 'Bus Assignments'
    
    def __str__(self):
        return f"{self.bus} on {self.route} - {self.date} {self.start_time}-{self.end_time}"
    
    def duration_hours(self):
        """Calculate the duration of this assignment in hours"""
        from datetime import datetime
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = (end - start).total_seconds() / 3600
        return round(duration, 1)