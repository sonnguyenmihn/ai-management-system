from django.http import JsonResponse
from functools import wraps
# from ..models import Token
from django.shortcuts import redirect
from django.utils import timezone
import json
from .decode_jwt import decode_jwt

# def token_required(f):
#     @wraps(f)
#     def decorated(request, *args, **kwargs):
#         # token = request.headers.get('Authorization')
#         # if not token:
#         #     return JsonResponse({'error': 'Token is missing!'}, status=402)
#         # try:
#         #     token = Token.objects.get(token=token)
#         # except:
#         #     return JsonResponse({'error': 'invalid token'})
#         # if not token.is_Usable():  # Custom method to check expiration (see below)
#         #     return redirect('login')
#         return f(request, *args, **kwargs)
#     return decorated

def token_required(f):
    @wraps(f)
    def decorated(request,*args,**kwargs):
        request_body = request.body.decode('utf-8')
        json_data = json.loads(request_body)
        JWT_token = json_data.get("headers")["Authorization"]
        if not JWT_token:
            return JsonResponse({'error':'invalid'})
        JWT_token = JWT_token.split()[1]
        decoded_JWT = decode_jwt(JWT_token)
        if decoded_JWT == "invalid":
            return JsonResponse({'error':'invalid'})
        else:
            return f(request,*args,**kwargs)
    return decorated