from django.shortcuts import render
from django.http import JsonResponse

import json

from common.serializers import AddressSerializer
from common.models import Address
from restaurants.models import Restaurant
from menus.models import Menu

def create(request):
    data = json.loads(request.body)
    name = data.get('name')
    address = data.get('address')
    if name == None:
        return JsonResponse({'detail' : 'Must supply restaurant name.'}, status = 400)
    if address == None:
        return JsonResponse({'detail' : 'Must supply restaurant address.'}, status = 400)
    addr_serializer = AddressSerializer(data = address)
    if not addr_serializer.is_valid():
        return JsonResponse({'detail' : 'Invalid address.'}, status = 400)
    addr = Address(**address)
    addr.save()
    restaurant = Restaurant(name = name, address = addr, owner = request.user)
    restaurant.save()
    menu = Menu(restaurant = restaurant)
    menu.save()
    return JsonResponse({'detail' : 'Successfully created restaurant.'})

def view(request):
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    return JsonResponse({'name' : restaurant.name})