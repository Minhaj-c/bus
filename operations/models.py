from django.db import models
from django.conf import settings  # <-- ADD THIS IMPORT
from schedules.models import Bus
from routes.models import Route
from decimal import Decimal

class WeeklyPerformance(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='weekly_performances')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='weekly_performances')
    week_start_date = models.DateField(help_text="The start date (Monday) of the week being recorded.")
    
    # The key metric: Manually entered total passengers for the week
    total_passengers = models.PositiveIntegerField(help_text="Total passengers carried on this route this week.")
    total_kms = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total kilometers traveled this week.")

    # Financials (Will be calculated automatically on save)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False) # Now editable=False
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)    # Now editable=False
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)   # Now editable=False

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['bus', 'route', 'week_start_date']
        ordering = ['-week_start_date', 'bus']

    def __str__(self):
        return f"{self.bus} - {self.route} - Week of {self.week_start_date}"

    # NEW SAVE METHOD WITH AUTOMATIC CALCULATION
    def save(self, *args, **kwargs):
        # 1. CALCULATE REVENUE
        # Assumption: The average passenger travels half the route's distance.
        # Use Decimal('0.5') instead of float 0.5 to avoid type errors
        average_journey_distance = self.route.total_distance * Decimal('0.5')
        self.total_revenue = self.total_passengers * average_journey_distance * Decimal(settings.TICKET_PRICE_PER_KM)
        
        # 2. CALCULATE COST
        # Fuel Used (liters) = Total Kilometers / Mileage (km/liter)
        # Convert settings to Decimal for consistent arithmetic
        fuel_used = self.total_kms / Decimal(self.bus.mileage)
        self.total_cost = fuel_used * Decimal(settings.FUEL_PRICE_PER_LITER)
        
        # 3. CALCULATE PROFIT
        self.total_profit = self.total_revenue - self.total_cost
        
        # Call the original save method
        super().save(*args, **kwargs)