from django.db import models
from django.conf import settings
from routes.models import Stop
from django.utils import timezone

class DemandAlert(models.Model):
    # The registered user submitting the report
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='demand_alerts')
    
    # The stop where people are waiting
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='demand_alerts')
    
    # The core data: number of people waiting at the stop (including the user)
    number_of_people = models.PositiveIntegerField()
    
    # Status for admin to track
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('verified', 'Verified'),
        ('dispatched', 'Bus Dispatched'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    # Automatically expire alerts after 1 hour
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField() # Set to 1 hour from creation

    def save(self, *args, **kwargs):
        # Set expiry time to 1 hour from creation if this is a new alert
        if not self.pk:  # If the object is being created (has no primary key yet)
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_active(self):
        """Check if the demand alert is still valid (not expired)"""
        return timezone.now() < self.expires_at

    class Meta:
        ordering = ['-created_at']  # Show newest alerts first

    def __str__(self):
        return f"{self.user.email}: {self.number_of_people} people at {self.stop.name}"