from django.shortcuts import render, redirect  # <-- ADD redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from .models import WeeklyPerformance
from django.db.models import Sum, Count  
from django.contrib import messages  # <-- ADD THIS IMPORT
from schedules.models import BusSchedule  # <-- ADD THESE IMPORTS
from preinforms.models import PreInform  # <-- ADD THIS IMPORT

def admin_check(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(admin_check)
def admin_dashboard(request):
    """View for the admin dashboard showing weekly performance summary"""
    
    # Calculate the start of last week (assuming week starts on Monday)
    today = timezone.now().date()
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    
    # Get all performance records from last week
    last_week_performances = WeeklyPerformance.objects.filter(
        week_start_date=start_of_last_week
    ).select_related('bus', 'route')
    
    # Calculate totals
    total_profit = sum(performance.total_profit for performance in last_week_performances)
    total_revenue = sum(performance.total_revenue for performance in last_week_performances)
    total_cost = sum(performance.total_cost for performance in last_week_performances)
    total_passengers = sum(performance.total_passengers for performance in last_week_performances)
    
    # Get top performing routes (by total profit)
    from django.db.models import Sum
    route_performance = last_week_performances.values('route__number', 'route__name').annotate(
        total_profit=Sum('total_profit'),
        total_passengers=Sum('total_passengers')
    ).order_by('-total_profit')
    
    # Get top performing buses (by total profit)
    bus_performance = last_week_performances.values('bus__number_plate').annotate(
        total_profit=Sum('total_profit'),
        total_routes=Count('id')
    ).order_by('-total_profit')
    
    context = {
        'week_start': start_of_last_week,
        'total_profit': total_profit,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_passengers': total_passengers,
        'route_performance': route_performance,
        'bus_performance': bus_performance,
        'performances': last_week_performances,
    }
    
    return render(request, 'admin_dashboard.html', context)

# NEW FUNCTION ADDED BELOW - DO NOT REMOVE EXISTING CODE ABOVE
@user_passes_test(admin_check)
def generate_weekly_report_view(request):
    """View that generates weekly reports (same functionality as the command)"""
    # Calculate last week's dates (Monday to Sunday)
    today = timezone.now().date()
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    
    report_data = []
    
    # Get all bus assignments from last week
    weekly_assignments = BusSchedule.objects.filter(
        date__gte=start_of_last_week,
        date__lte=end_of_last_week
    ).select_related('bus', 'route')
    
    if not weekly_assignments.exists():
        messages.warning(request, "No bus assignments found for last week. Create some BusSchedule records first.")
        return redirect('admin-dashboard')
    
    # Group assignments by bus and route
    from itertools import groupby
    from operator import attrgetter
    
    assignments_sorted = sorted(weekly_assignments, key=lambda x: (x.bus_id, x.route_id))
    
    for (bus, route), bus_assignments in groupby(assignments_sorted, key=lambda x: (x.bus, x.route)):
        bus_assignments = list(bus_assignments)
        
        # Calculate total kilometers for this bus on this route
        total_kms = sum(assignment.route.total_distance for assignment in bus_assignments)
        
        # Calculate ESTIMATED passengers from PreInform
        estimated_passengers = PreInform.objects.filter(
            route=route,
            date_of_travel__gte=start_of_last_week,
            date_of_travel__lte=end_of_last_week
        ).count()
        
        # Create or update weekly performance record
        weekly_perf, created = WeeklyPerformance.objects.get_or_create(
            bus=bus,
            route=route,
            week_start_date=start_of_last_week,
            defaults={
                'estimated_passengers': estimated_passengers,
                'total_kms': total_kms,
                'actual_passengers': 0
            }
        )
        
        report_data.append({
            'bus': bus,
            'route': route,
            'estimated_passengers': estimated_passengers,
            'total_kms': total_kms,
            'created': created
        })
    
    messages.success(request, f"Generated weekly report for {start_of_last_week} to {end_of_last_week}")
    return render(request, 'report_generated.html', {
        'report_data': report_data,
        'week_start': start_of_last_week,
        'week_end': end_of_last_week
    })