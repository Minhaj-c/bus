from django.db import models
from django.conf import settings
from schedules.models import Bus
from routes.models import Route
from decimal import Decimal

class WeeklyPerformance(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='weekly_performances')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='weekly_performances')
    week_start_date = models.DateField(help_text="The start date (Monday) of the week being recorded.")
    
    # NEW: SEPARATE PASSENGER COUNTS
    estimated_passengers = models.PositiveIntegerField(
        default=0,
        help_text="Estimated passengers from PreInform data (auto-calculated)"
    )
    actual_passengers = models.PositiveIntegerField(
        default=0,
        help_text="Actual passengers from ticket sales (manually entered)"
    )
    
    # KEEP EXISTING FIELD (for backward compatibility)
    total_passengers = models.PositiveIntegerField(
        help_text="Total passengers carried on this route this week. Auto-calculated from estimated + actual."
    )
    
    total_kms = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total kilometers traveled this week.")

    # Financials (Will be calculated automatically on save)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['bus', 'route', 'week_start_date']
        ordering = ['-week_start_date', 'bus']

    def __str__(self):
        return f"{self.bus} - {self.route} - Week of {self.week_start_date}"

    # UPDATED SAVE METHOD
    def save(self, *args, **kwargs):
        # Auto-calculate total_passengers as sum of estimated + actual
        self.total_passengers = self.estimated_passengers + self.actual_passengers
        
        # Use ACTUAL passengers for revenue calculation if available, otherwise use estimated
        passengers_for_revenue = self.actual_passengers if self.actual_passengers > 0 else self.estimated_passengers
        
        # 1. CALCULATE REVENUE
        average_journey_distance = self.route.total_distance * Decimal('0.5')
        self.total_revenue = passengers_for_revenue * average_journey_distance * Decimal(settings.TICKET_PRICE_PER_KM)
        
        # 2. CALCULATE COST
        fuel_used = self.total_kms / Decimal(self.bus.mileage)
        self.total_cost = fuel_used * Decimal(settings.FUEL_PRICE_PER_LITER)
        
        # 3. CALCULATE PROFIT
        self.total_profit = self.total_revenue - self.total_cost
        
        # Call the original save method
        super().save(*args, **kwargs)