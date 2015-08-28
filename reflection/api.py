import json
from django.http import JsonResponse

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import signing


def create_token(username, password):
    return signing.dumps((username, password))


def get_user_from_token(token):
    username, password = signing.loads(token)
    return authenticate(username=username, password=password)


def register(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    User.objects.create_user(username, email, password)
    return JsonResponse({'token': create_token(username, password)})


def create_event(request):
    data = json.loads(request.body)
    get_user_from_token(data.get('token'))
    return JsonResponse({'success': 'true'})


def login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'Authentication failed.'}, code=403)
    else:
        return JsonResponse({'token': create_token(username, password)})
