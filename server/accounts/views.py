from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User

from rest_framework import serializers

import json

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required = True, max_length = 50)
    password = serializers.CharField(required = True, max_length = 50)

@require_POST
def signup(request):
    data = json.loads(request.body)
    if not SignupSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    username = data.get('username')
    password = data.get('password')
    if User.objects.filter(username = username).first():
        return JsonResponse({'detail' : 'Username is already taken.'}, status = 400)
    User.objects.create_user(username = username, password = password).save()
    return JsonResponse({'detail' : 'Successfully signed up.'})

class DeleteSerializer(serializers.Serializer):
    password = serializers.CharField(required = True, max_length = 50)

@require_POST
def delete(request):
    data = json.loads(request.body)
    if not DeleteSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    password = data.get('password')
    user = authenticate(username = request.user.username, password = password)
    if not user:
        return JsonResponse({'detail' : 'Invalid password.'}, status = 400)
    user.delete()
    return JsonResponse({'detail' : 'Successfully deleted account.'})

@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse({'detail' : 'Please provide username and password.'}, status=400)
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'detail' : 'Invalid credentials.'}, status=400)
    login(request, user)
    return JsonResponse({'detail' : 'Successfully logged in.'})

def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail' : 'You\'re not logged in.'}, status=400)
    logout(request)
    return JsonResponse({'detail' : 'Successfully logged out.'})

@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated' : False})
    return JsonResponse({'isAuthenticated' : True})

def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated' : False})
    return JsonResponse({'username' : request.user.username})