from django.shortcuts import render, redirect  
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from .models import WeeklyPerformance
from django.db.models import Sum, Count  
from django.contrib import messages  
from schedules.models import BusSchedule  
from preinforms.models import PreInform  

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
    


@user_passes_test(admin_check)
def analytics_dashboard(request):
    """Advanced analytics dashboard with trends and patterns"""
    
    today = timezone.now().date()
    start_date = today - timedelta(weeks=8)
    
    # 1. Weekly Trends
    weekly_data = WeeklyPerformance.objects.filter(
        week_start_date__gte=start_date
    ).values('week_start_date')
    
    weekly_trends = []
    for week in weekly_data.distinct():
        week_start = week['week_start_date']
        week_data = WeeklyPerformance.objects.filter(week_start_date=week_start)
        
        weekly_trends.append({
            'week_start_date': week_start,
            'total_profit': sum(p.total_profit for p in week_data),
            'total_revenue': sum(p.total_revenue for p in week_data),
            'total_passengers': sum(p.total_passengers for p in week_data),
        })
    
    # 2. Route Performance
    route_data = []
    for performance in WeeklyPerformance.objects.filter(week_start_date__gte=start_date):
        found = False
        for item in route_data:
            if item['route__number'] == performance.route.number:
                item['total_profit'] += performance.total_profit
                item['total_kms'] += performance.total_kms
                item['total_passengers'] += performance.total_passengers
                found = True
                break
        
        if not found:
            route_data.append({
                'route__number': performance.route.number,
                'route__name': performance.route.name,
                'total_profit': performance.total_profit,
                'total_kms': performance.total_kms,
                'total_passengers': performance.total_passengers,
            })
    
    for item in route_data:
        item['profit_per_km'] = item['total_profit'] / item['total_kms'] if item['total_kms'] > 0 else 0
    
    route_performance = sorted(route_data, key=lambda x: x['total_profit'], reverse=True)[:10]
    
    # 3. Bus Efficiency
    bus_data = []
    for performance in WeeklyPerformance.objects.filter(week_start_date__gte=start_date):
        found = False
        for item in bus_data:
            if item['bus__number_plate'] == performance.bus.number_plate:
                item['total_profit'] += performance.total_profit
                item['total_revenue'] += performance.total_revenue
                item['total_kms'] += performance.total_kms
                item['total_passengers'] += performance.total_passengers
                found = True
                break
        
        if not found:
            bus_data.append({
                'bus__number_plate': performance.bus.number_plate,
                'total_profit': performance.total_profit,
                'total_revenue': performance.total_revenue,
                'total_kms': performance.total_kms,
                'total_passengers': performance.total_passengers,
            })
    
    for item in bus_data:
        item['revenue_per_km'] = item['total_revenue'] / item['total_kms'] if item['total_kms'] > 0 else 0
    
    bus_efficiency = sorted(bus_data, key=lambda x: x['revenue_per_km'], reverse=True)[:10]
    
    # 4. Demand Patterns (Fixed for SQLite)
    from django.db.models.functions import ExtractHour, ExtractWeekDay
    demand_patterns = (
        PreInform.objects.filter(created_at__gte=start_date)
        .annotate(hour=ExtractHour('desired_time'))
        .annotate(day_of_week=ExtractWeekDay('date_of_travel'))
        .values('hour', 'day_of_week')
        .annotate(demand_count=Count('id'))
        .order_by('day_of_week', 'hour')
    )
    
    context = {
        'weekly_trends': weekly_trends,
        'route_performance': route_performance,
        'bus_efficiency': bus_efficiency,
        'demand_patterns': list(demand_patterns),
    }
    
    return render(request, 'analytics_dashboard.html', context)