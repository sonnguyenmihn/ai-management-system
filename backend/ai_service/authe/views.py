from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from object_detection.models import *
from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    # Check if user already exists
    try:
        user = User.objects.get(username=username)
        return JsonResponse({'error': 'User already exists'}, status=409)
    except ObjectDoesNotExist:
        # Hash the password
        hashed_password = password
        # Create new user
        user = User.objects.create(username=username, password_hash=hashed_password)
        user.save()
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User created successfully'
        }, status=201)

@api_view(['POST'])
def login(request):
    print('received')
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    try:
        # Check user in the database
        user = User.objects.get(username=username)
        # Verify password
        if password == user.password_hash:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            })
        else:
            return JsonResponse({'error': 'Invalid password'}, status=401)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)

@api_view(['POST'])
def test(request):
    print(request)
    return JsonResponse({})