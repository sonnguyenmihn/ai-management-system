from .models import *

services = AIService.objects.all()
service_stats = []

for service in services:
# Calculate total enterprise requests and profit from enterprise requests
    total_profit = 0
    total_requests = 0
    enterprise_requests = RequestHistory.objects.filter(
        service=service,
        user__subscription__type='Enterprise'
    ).count()

    enterprise_profit = service.enterprise_price_per_request * enterprise_requests

    # Calculate total monthly subscriptions and profit
    monthly_requests = RequestHistory.objects.filter(
        service=service,
        user__subscription__type='Monthly'
    ).count()

    monthly_profit = service.monthly_price * monthly_requests

    # Calculate total yearly subscriptions and profit
    yearly_requests = RequestHistory.objects.filter(
        service=service,
        user__subscription__type='yearly'
    ).count()

    yearly_profit = service.yearly_price * yearly_requests

    # Calculate total requests (all types)
    total_requests = enterprise_requests + monthly_requests + yearly_requests

    # Calculate total profit
    total_profit = enterprise_profit + monthly_profit + yearly_profit

    # Create a dictionary for the service statistics
    service_stat = {
        'service_name': service.name,
        'total_enterprise_requests': enterprise_requests,
        'total_monthly_subscriptions': monthly_requests,
        'total_yearly_subscriptions': yearly_requests,
        'total_requests': total_requests,
        'total_profit': total_profit,
    }

    # Append the service statistics to the list
    service_stats.append(service_stat)
    
    print(service_stats)
