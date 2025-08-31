from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from schedules.models import BusSchedule
from operations.models import WeeklyPerformance
from preinforms.models import PreInform

class Command(BaseCommand):
    help = 'Automatically generates weekly performance reports for all buses'
    
    def handle(self, *args, **options):
        # Calculate last week's dates (Monday to Sunday)
        today = timezone.now().date()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        
        self.stdout.write(f"📊 Generating weekly report for {start_of_last_week} to {end_of_last_week}")
        
        # Get all bus assignments from last week
        weekly_assignments = BusSchedule.objects.filter(
            date__gte=start_of_last_week,
            date__lte=end_of_last_week
        ).select_related('bus', 'route')
        
        # Group assignments by bus and route (since your model has both)
        from itertools import groupby
        from operator import attrgetter
        
        # Sort by both bus and route since your WeeklyPerformance requires both
        assignments_sorted = sorted(weekly_assignments, key=lambda x: (x.bus_id, x.route_id))
        
        for (bus, route), bus_assignments in groupby(assignments_sorted, key=lambda x: (x.bus, x.route)):
            bus_assignments = list(bus_assignments)
            
            # 1. Calculate total kilometers for this bus on this route
            total_kms = sum(assignment.route.total_distance for assignment in bus_assignments)
            
            # 2. Calculate ESTIMATED passengers from PreInform for this specific route
            estimated_passengers = PreInform.objects.filter(
                route=route,  # Specific to this route
                date_of_travel__gte=start_of_last_week,
                date_of_travel__lte=end_of_last_week
            ).count()
            
            # 3. Create weekly performance record for this bus + route combination
            weekly_perf, created = WeeklyPerformance.objects.get_or_create(
                bus=bus,
                route=route,  # Your model requires route
                week_start_date=start_of_last_week,
                defaults={
                    'estimated_passengers': estimated_passengers,
                    'total_kms': total_kms,
                    'actual_passengers': 0  # Start with 0, admin will update
                }
            )
            
            if created:
                self.stdout.write(f"✅ Created: {bus} on {route} - {estimated_passengers} est. passengers, {total_kms} km")
            else:
                self.stdout.write(f"📝 Updated: {bus} on {route} - {estimated_passengers} est. passengers added")
        
        self.stdout.write("🎉 Weekly report generation completed! Admin can now add actual ticket numbers.")