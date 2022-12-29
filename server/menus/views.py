from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core import serializers

from restaurants.models import Restaurant
from menus.models import MenuItem

from rest_framework import serializers

import json

def view(request):
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    query = MenuItem.objects.filter(menu = restaurant.menu)
    item_list = []
    for item in query:
        item_list.append({'name' : item.name, 'description' : item.description, 'price' : item.price, 'uuid' : item.uuid})
    return JsonResponse(item_list, safe = False)

class AddFormSerializer(serializers.Serializer):
    name = serializers.CharField(required = True, max_length = 100)
    description = serializers.CharField(required = False, max_length = 500, allow_blank = True)
    price = serializers.DecimalField(required = True, max_digits = 10, decimal_places = 2)

def add(request):
    data = json.loads(request.body)
    if not AddFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    name = data.get('name')
    description = data.get('description')
    if not description:
        description = ''
    price = data.get('price')
    if name == None or description == None or price == None:
        return JsonResponse({'detail' : 'Missing one or more essential fields.'}, status = 400)
    item = MenuItem(name = name, description = description, price = price, menu = restaurant.menu)
    item.save()
    return JsonResponse({'detail' : 'Successfully created menu item.'})

class ModifyFormSerializer(serializers.Serializer):
    name = serializers.CharField(required = True, max_length = 100)
    description = serializers.CharField(required = False, max_length = 500, allow_blank = True)
    price = serializers.DecimalField(required = True, max_digits = 10, decimal_places = 2)
    uuid = serializers.UUIDField(required = True)

def modify(request):
    data = json.loads(request.body)
    if not ModifyFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    name = data.get('name')
    description = data.get('description')
    if not description:
        description = ''
    price = data.get('price')
    uuid = data.get('uuid')
    if name == None or description == None or price == None or uuid == None:
        return JsonResponse({'detail' : 'Missing one or more essential fields.'}, status = 400)
    item = MenuItem.objects.filter(uuid = uuid).first()
    if item == None or item.menu != restaurant.menu:
        return JsonResponse({'detail' : 'There is no menu item matching the specified UUID.'}, status = 400)
    item.name = name
    item.description = description
    item.price = price
    item.uuid = uuid
    item.save()
    return JsonResponse({'detail' : 'Successfully modified menu item.'})

class RemoveFormSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required = True)

def remove(request):
    data = json.loads(request.body)
    if not RemoveFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    item_id = data.get('uuid')
    if item_id == None:
        return JsonResponse({'detail' : 'Must specify item ID.'}, status = 400)
    query = MenuItem.objects.filter(uuid = item_id)
    item = query.first()
    if item == None or item.menu != restaurant.menu:
        return JsonResponse({'detail' : 'Item with specified ID does not exist.'}, status = 400)
    item.delete()
    return JsonResponse({'detail' : 'Successfully removed menu item.'})