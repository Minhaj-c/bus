from django.db import models
from django.conf import settings
from routes.models import Route, Stop

class PreInform(models.Model):
    # User who is submitting the travel plan
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preinforms')
    
    # The route the user intends to take
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='preinforms')
    
    # The user's desired date and time of travel
    date_of_travel = models.DateField()  # e.g., Tomorrow
    desired_time = models.TimeField()    # e.g., 1:00 AM
    
    # The stop where the user will board
    boarding_stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        related_name='boarding_passengers'
    )
    
    # Number of passengers
    passenger_count = models.PositiveIntegerField(default=1)
    
    # Status of the pre-inform
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('noted', 'Noted by Controller'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Show newest requests first

    def __str__(self):
        return f"{self.user.email} on {self.date_of_travel} at {self.desired_time} (Route {self.route.number})"