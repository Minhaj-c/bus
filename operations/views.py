from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from .models import WeeklyPerformance
from django.db.models import Sum, Count  

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