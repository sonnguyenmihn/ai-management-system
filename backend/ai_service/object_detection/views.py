from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from .tasks import ai_service
import json
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
# from authe.models import Token, ModelAi, UserPermission
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from .models import *
from django.template import loader
from django.db.models import Q
from authe.functions.token_required import token_required
from authe.functions.decode_jwt import decode_jwt
import base64
from .functions.CreateChart import *



@token_required
@api_view(["POST"])
def user_subscribe(request):
    try:
        type = request.data["headers"]["subscriptionType"]
        serviceName = request.data["headers"]["serviceName"]
        service=AIService.objects.get(name=serviceName)
        token = request.data["headers"]["Authorization"]
        if not token:
            return JsonResponse({'error':'invalid'})
        token = token.split()[1]
        user_id = decode_jwt(token)
        user = User.objects.get(pk=user_id)
        new_sub = Subscription(user=user, service=service, type=type,date_subscribed=timezone.now(), active = "Pending")
        new_sub.set_date_ended()  # Set the end date based on subscription type
        new_sub.save()
        return JsonResponse({'message': 'Subscription successful'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@token_required
@api_view(["POST"])
def user_delete_service(request):
    token = request.data["headers"]["Authorization"]
    if not token:
        return JsonResponse({'error':'invalid'})
    token = token.split()[1]
    user_id = decode_jwt(token)
    user = User.objects.get(pk=user_id)
    
    service = request.data["headers"]["serviceName"]
    service = AIService.objects.get(name=service)
    subscription = Subscription.objects.get(active="Approved", user = user, service=service)
    subscription.active = "Cancelled"
    subscription.save()
    return JsonResponse({})

@token_required
@api_view(['POST'])
def user_check(request, type_):
    token = request.data["headers"]["Authorization"]
    if not token:
        return JsonResponse({'error':'invalid'})
    token = token.split()[1]
    user_id = decode_jwt(token)
    user = User.objects.get(pk=user_id)
    if type_ == "dashboard":
        subscriptions = Subscription.objects.filter(user=user)
        total_bill = 0
        service_request_counts = []
        total_request = 0
        for subscription in subscriptions:
            service = subscription.service
            subscription_type = subscription.type
            subscription_price = 0

            # Calculate total requests for this subscription
            total_requests = RequestHistory.objects.filter(user=user, service=service, subscription = subscription).count()
            # Calculate total price based on subscription type
            if subscription_type == 'Enterprise' or subscription_type =="enterprise":
                subscription_price = total_requests * service.enterprise_price_per_request
            elif subscription_type == 'Monthly' or subscription_type=="monthly":
                subscription_price = service.monthly_price
            elif subscription_type == 'Yearly' or subscription_type == "yearly":
                subscription_price = service.yearly_price

            # Accumulate total bill
            total_bill += subscription_price
            total_request += total_requests
        total_requests = RequestHistory.objects.filter(user=user).count()
        successful_requests = RequestHistory.objects.filter(user=user, status='SUCCESS').count()
        if total_requests > 0:
            success_rate = (successful_requests / total_requests) * 100
        else:
            success_rate = 100  # Handle division by zero
        approved_subscriptions = Subscription.objects.filter(
            Q(user=user) & 
            (Q(active="Cancelled") | Q(active="Approved"))
        )    
        approved_services = AIService.objects.filter(subscription__in=approved_subscriptions).distinct()
        for service in approved_services:
            count = RequestHistory.objects.filter(user=user, service = service).count()
            service_request_counts.append({
                'name':service.name,
                'num_requests': count,
            })
            
            
        chart1 = create_request_per_service_chart(service_request_counts)
        chart2 = create_success_rate_chart(success_rate)
        return JsonResponse({
            'request_per_service' : service_request_counts,
            'total_price': total_bill,
            "total_request": total_request,
            "success_rate" : success_rate,
            "chart1" : chart1,
            "chart2": chart2,
        })
        
        
    elif type_ == "history":
        history_entries = RequestHistory.objects.filter(user=user)
        
        history_data = []
        for entry in history_entries:
            history_data.append({
                'user': entry.user.username,
                'service': entry.service.name,
                'subscription': entry.subscription.id if entry.subscription else None,
                'request_time': entry.request_time.isoformat(),
                'status': entry.status,
                'processing_time': entry.processing_time
            })

        return JsonResponse({'history': history_data})
    elif type_ == "services":
        print("received")
        subscriptions = Subscription.objects.filter(user=user, active="Approved")
        subscriptions_pending = Subscription.objects.filter(user=user, active="Pending")

        subscribed_services = []
        subscription_details = []
        pending_services = []

        #update status
        for subscription in subscriptions:
            subscription.update_active_status()
            
        subscriptions = Subscription.objects.filter(user=user, active="Approved")
        for subscription in subscriptions:
            service = subscription.service
            subscribed_services.append({
                'id': service.id_service,
                'name': service.name,
                'description': service.description,
                'monthly_price': service.monthly_price,
                'yearly_price': service.yearly_price,
                'enterprise_price_per_request': service.enterprise_price_per_request,
            })
            subscription_details.append({
                'service_id': service.id_service,
                'date_subscribed': subscription.date_subscribed,
                'date_ended': subscription.date_ended,
                'active': subscription.active,
                'type': subscription.type,
            })
            
            # Process pending subscriptions
        for subscription in subscriptions_pending:
            service = subscription.service
            pending_services.append({
                'id': service.id_service,
                'name': service.name,
                'description': service.description,
                'monthly_price': service.monthly_price,
                'yearly_price': service.yearly_price,
                'enterprise_price_per_request': service.enterprise_price_per_request,
                'active': subscription.active,
                'type': subscription.type,
            })

        # Fetch all services
        all_services = AIService.objects.all()
        # Identify services not subscribed to
        non_subscribed_services = []
        for service in all_services:
            if service not in [sub.service for sub in subscriptions] and service not in [sub.service for sub in subscriptions_pending]:
                non_subscribed_services.append({
                    'id': service.id_service,
                    'name': service.name,
                    'description': service.description,
                    'monthly_price': service.monthly_price,
                    'yearly_price': service.yearly_price,
                    'enterprise_price_per_request': service.enterprise_price_per_request,
                })
                
        return JsonResponse({
            'subscribed_services': subscribed_services,
            'subscription_details': subscription_details,
            'non_subscribed_services': non_subscribed_services,
            'pending_services': pending_services,
        })
    elif type_ == "request":
        # Fetch all approved subscriptions for the user
        subscriptions = Subscription.objects.filter(user=user, active="Approved")
        
        # Update active status of each subscription based on your logic
        for subscription in subscriptions:
            subscription.update_active_status()
        
        # Re-fetch approved subscriptions to ensure updated status
        approved_subscriptions = Subscription.objects.filter(user=user, active='Approved')
        
        # Fetch distinct approved services related to these subscriptions
        approved_services = AIService.objects.filter(subscription__in=approved_subscriptions).distinct()
        if not approved_services:
            return JsonResponse({'error': 'invalid'})
        
        # Prepare JSON response with a list of approved services
        approved_services_list = list(approved_services.values("name"))  # Convert queryset to list of dictionaries
        
        return JsonResponse({'approved_services': approved_services_list})
    else:
        return JsonResponse({'error' : 'invalid!'})
        


@api_view(['POST','GET'])
def admin_ai_service(request):
    if request.method == 'GET':
        services = AIService.objects.all()
        template = loader.get_template('ai_service.html')
        context = {
            'services': services
        }
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        id_service = request.POST.get("id_service")
        name = request.POST.get('name')
        description = request.POST.get('description')
        monthly_price = request.POST.get('monthly_price')
        yearly_price = request.POST.get('yearly_price')
        enterprise_price_per_request = request.POST.get('enterprise_price_per_request')
        url = request.POST.get('url')
        try:
            services = AIService.objects.filter(id_service=id_service)
            if not services.exists():
                new_service = AIService(
                    url = url,
                    id_service = id_service,
                    name=name,
                    description=description,
                    monthly_price=monthly_price,
                    yearly_price=yearly_price,
                    enterprise_price_per_request=enterprise_price_per_request
                )
                new_service.save()
        except Exception as e:
            print(e)
        return redirect('admin_ai_service')
        
@api_view(["POST"])
def admin_ai_service_delete(request):
    id_service = request.POST.get("id_service")
    service = AIService.objects.get(id_service=id_service)
    service.delete()
    return redirect('admin_ai_service')

@api_view(['POST','GET'])
def admin_users(request):
    if request.method == "GET":
        users = User.objects.values('username')
        template = loader.get_template('users.html')
        context = {
            'users' : users
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username)
        user.delete()
        return redirect('admin_users')

def admin_users_detail(request, username):
    template = loader.get_template('user_detail.html')
    user = User.objects.get(username=username)
    subscriptions = Subscription.objects.filter(
    Q(user=user) & 
    (Q(active="Cancelled") | Q(active="Approved"))
)    
    total_bill = 0
    billing_details = []

    for subscription in subscriptions:
        service = subscription.service
        subscription_type = subscription.type
        subscription_price = 0

        # Calculate total requests for this subscription
        total_requests = RequestHistory.objects.filter(user=user, service=service, subscription = subscription).count()

        # Calculate total price based on subscription type
        if subscription_type == 'Enterprise' or subscription_type == "enterprise":
            subscription_price = total_requests * service.enterprise_price_per_request
        elif subscription_type == 'Monthly' or subscription_type == "monthly":
            subscription_price = service.monthly_price
        elif subscription_type == 'Yearly' or subscription_type == "yearly":
            subscription_price = service.yearly_price

        # Create billing detail entry
        billing_detail = {
            'date_subscribed': subscription.date_subscribed,
            'date_ended': subscription.date_ended,
            'total_price': subscription_price,
            'type': subscription_type,
            'service': service.name,
            'total_requests': total_requests,
        }
        billing_details.append(billing_detail)

        # Accumulate total bill
        total_bill += subscription_price
    
    subscriptions_pending = Subscription.objects.filter(user=user, active="Pending")
    
    history_entries = RequestHistory.objects.filter(user=user)
    
    
    context = {
        'history' : history_entries,
        'user': user,
        'total_bill':total_bill,
        'billing_details':billing_details,
        'pending' : subscriptions_pending,
    }
    return HttpResponse(template.render(context, request))

@api_view(['POST','GET'])
def admin_user_detail_approve(request):
    try:
        username = request.POST.get("user")
        service_name = request.POST.get("service_name")
        user = User.objects.get(username=username)
        service = AIService.objects.get(name=service_name)
        sub = Subscription.objects.get(user=user, service=service, active="Pending")
        sub.active = "Approved"
        sub.save()
        return redirect(reverse('admin_users_detail', args=(username,)))
    except (User.DoesNotExist, AIService.DoesNotExist, Subscription.DoesNotExist) as e:
        return HttpResponse(str(e), status=404)


@api_view(['POST','GET'])
def admin_user_detail_delete(request):
    try:
        username = request.POST.get("user")
        service_name = request.POST.get("service_name")
        user = User.objects.get(username=username)
        service = AIService.objects.get(name=service_name)
        sub = Subscription.objects.get(user=user, service=service, active="Pending")
        sub.delete()
        return redirect(reverse('admin_users_detail', args=(username,)))
    except (User.DoesNotExist, AIService.DoesNotExist, Subscription.DoesNotExist) as e:
        return HttpResponse(str(e), status=404)

@api_view(['POST','GET'])
def admin_profit(request):
    services = AIService.objects.all()
    service_stats = []

    for service in services:
        # Calculate total enterprise requests and profit from enterprise requests
        total_profit = 0
        total_requests = 0
        enterprise_requests = RequestHistory.objects.filter(
            service=service,
            subscription__type = 'enterprise'
        ).count()

        enterprise_profit = service.enterprise_price_per_request * enterprise_requests

        # Calculate total monthly subscriptions and profit
        monthly_sub = Subscription.objects.filter(
            service=service,
            type='monthly',
        ).count()
        
        monthly_requests = RequestHistory.objects.filter(
            service=service,
            subscription__type='monthly',
        ).count()

        monthly_profit = service.monthly_price * monthly_sub

        # Calculate total yearly subscriptions and profit
        yearly_sub = Subscription.objects.filter(
            service=service,
            type='yearly',
        ).count()
        
        yearly_requests = RequestHistory.objects.filter(
            service=service,
            subscription__type='yearly',
        ).count()

        yearly_profit = service.yearly_price * yearly_sub

        # Calculate total requests (all types)
        total_requests = enterprise_requests + monthly_requests + yearly_requests

        # Calculate total profit
        total_profit = enterprise_profit + monthly_profit + yearly_profit

        # Create a dictionary for the service statistics
        service_stat = {
            'service_name': service.name,
            'total_enterprise_requests': enterprise_requests,
            'total_monthly_subscriptions': monthly_sub,
            'total_yearly_subscriptions': yearly_sub,
            'total_requests': total_requests,
            'total_profit': total_profit,
        }

        # Append the service statistics to the list
        service_stats.append(service_stat)
    context = {
        'service_stats' : service_stats
    }
    template = loader.get_template("profits.html")
    return HttpResponse(template.render(context, request))

@token_required
@api_view(["POST"])
def test(request):
    print(request.data["headers"]["service"]["name"])
    
    return JsonResponse({"message": "Image saved successfully"})

@token_required
@api_view(["POST"])
def user_ai_service_airplane(request):
    #get user
    token = request.data["headers"]["Authorization"]
    if not token:
        return JsonResponse({'error':'invalid'})
    token = token.split()[1]
    user_id = decode_jwt(token)
    user = User.objects.get(pk=user_id)
    
    #get base64 img
    img_base64 = request.data["headers"]["image_base64"]
    if not img_base64:
        return JsonResponse({'error': 'No image provided'}, status=400)

    service_name = 'airplane'
    service = AIService.objects.get(name=service_name)
    id_service = AIService.objects.filter(name=service_name).values('id_service').get()
    id_service = id_service['id_service']    
    
    # check approved subscription
    subscription = Subscription.objects.get(
    user=user,
    service=service,
    active='Approved'
    )
    if not subscription:
        return JsonResponse({'error': 'No valid subscription found'}, status=403)
    
    #load user data to ai model
    predicted_photo = ai_service.delay(img_base64, id_service)
    
    # If you need the result immediately and it's quick to process, use get() carefully.
    result = predicted_photo.get()  # Specify timeout to avoid indefinite waiting
    
    
    ret_image = result[0]
    ret_speed = result[1]
    ret_status = predicted_photo.status
    requestHistory = RequestHistory(user=user, service = service, status = ret_status, processing_time=ret_speed, subscription=subscription)
    requestHistory.save()
    
    return JsonResponse({'image' : ret_image,'status': 'success'})

@token_required
@api_view(["POST"])
def user_ai_service_ship(request):
    #get user
    token = request.data["headers"]["Authorization"]
    if not token:
        return JsonResponse({'error':'invalid'})
    token = token.split()[1]
    user_id = decode_jwt(token)
    user = User.objects.get(pk=user_id)
    
    #get base64 img
    img_base64 = request.data["headers"]["image_base64"]
    if not img_base64:
        return JsonResponse({'error': 'No image provided'}, status=400)

    service_name = 'ship'
    service = AIService.objects.get(name=service_name)
    id_service = AIService.objects.filter(name=service_name).values('id_service').get()
    id_service = id_service['id_service']    
    
    # check approved subscription
    subscription = Subscription.objects.get(
    user=user,
    service=service,
    active='Approved'
    )
    if not subscription:
        return JsonResponse({'error': 'No valid subscription found'}, status=403)
    
    #load user data to ai model
    predicted_photo = ai_service.delay(img_base64, id_service)
    
    # If you need the result immediately and it's quick to process, use get() carefully.
    result = predicted_photo.get()  # Specify timeout to avoid indefinite waiting
    
    
    ret_image = result[0]
    ret_speed = result[1]
    ret_status = predicted_photo.status
    requestHistory = RequestHistory(user=user, service = service, status = ret_status, processing_time=ret_speed, subscription=subscription)
    requestHistory.save()
    
    return JsonResponse({'image' : ret_image,'status': 'success'})