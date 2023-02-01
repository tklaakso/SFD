from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import serializers

from orders.models import Order
from .models import Driver, DriverOrder
from geo.models import Location

from .selection import on_new_driver
from .selection import lock as selection_lock

import json

class SignupSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required = True)
    longitude = serializers.FloatField(required = True)

def signup(request):
    data = json.loads(request.body)
    if not SignupSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    if Driver.objects.filter(user = request.user).count() > 0:
        return JsonResponse({'detail' : 'You are already a driver.'}, status = 400)
    location = Location(latitude = latitude, longitude = longitude)
    location.save()
    driver = Driver(user = request.user, home_location = location)
    driver.save()
    on_new_driver(driver)
    return JsonResponse({'detail' : 'You are now a driver.'})

def recommended(request):
    driver = Driver.objects.filter(user = request.user).first()
    if not driver:
        return JsonResponse({'detail' : 'You are not a driver.'}, status = 400)
    order_list = []
    for order in driver.recommended.all():
        order_list.append(order.serialize())
    return JsonResponse(order_list, safe = False)

class AcceptDeclineSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required = True)

def accept(request):
    driver = Driver.objects.filter(user = request.user).first()
    if not driver:
        return JsonResponse({'detail' : 'You are not a driver.'}, status = 400)
    data = json.loads(request.body)
    if not AcceptDeclineSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    uuid = data.get('uuid')
    order = DriverOrder.objects.filter(driver_recommended = driver, order__uuid = uuid).first()
    if not order:
        return JsonResponse({'detail' : 'Order with specified UUID does not exist.'}, status = 400)
    selection_lock.acquire()
    if driver.recommended.contains(order):
        driver.accept(order)
        selection_lock.release()
    else:
        selection_lock.release()
        return JsonResponse({'detail' : 'Cannot accept unrecommended order.'}, status = 400)
    return JsonResponse({'detail' : 'Accepted order.'})

def decline(request):
    driver = Driver.objects.filter(user = request.user).first()
    if not driver:
        return JsonResponse({'detail' : 'You are not a driver.'}, status = 400)
    data = json.loads(request.body)
    if not AcceptDeclineSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    uuid = data.get('uuid')
    query = DriverOrder.objects.filter(order__uuid = uuid)
    order = (query.filter(driver_recommended = driver) | query.filter(driver_accepted = driver)).first()
    if not order:
        return JsonResponse({'detail' : 'Order with specified UUID does not exist.'}, status = 400)
    selection_lock.acquire()
    if driver.recommended.contains(order) or driver.accepted.contains(order):
        driver.decline(order)
        selection_lock.release()
    else:
        selection_lock.release()
        return JsonResponse({'detail' : 'Order must be either recommended or accepted in order to decline.'}, status = 400)
    return JsonResponse({'detail' : 'Declined order.'})
