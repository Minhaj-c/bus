from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from schedules.models import Bus, BusSchedule, Route
from preinforms.models import PreInform
from operations.models import WeeklyPerformance
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates 8 weeks of sample data for ML training'
    
    def handle(self, *args, **options):
        self.stdout.write("📊 Creating 8 weeks of sample data...")
        
        # Clear existing data
        WeeklyPerformance.objects.all().delete()
        PreInform.objects.all().delete()
        BusSchedule.objects.all().delete()
        
        today = timezone.now().date()
        buses = list(Bus.objects.all())
        routes = list(Route.objects.all())
        User = get_user_model()
        
        # Get or create a test user for pre-informs
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={'role': 'passenger', 'password': 'testpass123'}
        )
        
        if not buses or not routes:
            self.stdout.write("❌ Please create some buses and routes first!")
            return
        
        # Create 8 weeks of data
        for week_offset in range(8, 0, -1):
            start_of_week = today - timedelta(weeks=week_offset)
            
            # Create bus assignments for this week
            for day_offset in range(7):
                current_date = start_of_week + timedelta(days=day_offset)
                
                # Assign each bus to 2-3 routes per day
                for bus in buses:
                    for _ in range(random.randint(2, 3)):
                        route = random.choice(routes)
                        BusSchedule.objects.create(
                            bus=bus,
                            route=route,
                            date=current_date,
                            start_time=random.choice(['08:00', '10:00', '14:00', '16:00']),
                            end_time=random.choice(['10:00', '12:00', '16:00', '18:00'])
                        )
            
            # Create PreInform data (passenger demand)
            for route in routes:
                # Base demand + random variation
                demand = random.randint(20, 100) + (week_offset * 10)
                for _ in range(demand):
                    PreInform.objects.create(
                        user=test_user,  # Use the test user instead of None
                        route=route,
                        date_of_travel=start_of_week + timedelta(days=random.randint(0, 6)),
                        desired_time=f"{random.randint(8, 18)}:00:00",
                        boarding_stop=random.choice(route.stops.all()),
                        passenger_count=random.randint(1, 4)
                    )
            
            self.stdout.write(f"✅ Created data for week {week_offset}")
        
        self.stdout.write("🎉 Sample data creation completed! Run generate-report to create weekly performance data.")