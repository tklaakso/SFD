from django.shortcuts import render
from django.http import JsonResponse

import json

from common.serializers import AddressSerializer
from common.models import Address
from restaurants.models import Restaurant
from menus.models import Menu, MenuItem
from geo.models import UserAddress, Location

from rest_framework import serializers

from geographic.interface import GeographicInterface

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
    with GeographicInterface() as inter:
        latlng = inter.geocode(str(addr))
    if not latlng:
        return JsonResponse({'detail' : 'We couldn\'t geocode your address.'}, status = 400)
    location_data = {'latitude' : latlng[0], 'longitude' : latlng[1]}
    location = Location(**location_data)
    location.save()
    restaurant = Restaurant(name = name, address = addr, owner = request.user, location = location)
    restaurant.save()
    menu = Menu(restaurant = restaurant)
    menu.save()
    return JsonResponse({'detail' : 'Successfully created restaurant.'})

def delete(request):
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if not restaurant:
        return JsonResponse({'detail' : 'You do not own a restaurant'}, status = 400)
    restaurant.delete()
    return JsonResponse({'detail' : 'Restaurant deleted successfully.'})

def view(request):
    query = Restaurant.objects.filter(owner = request.user)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'You do not own a restaurant.'}, status = 400)
    return JsonResponse({'name' : restaurant.name})

def browse(request):
    data = json.loads(request.body)
    if not AddressSerializer(data = data).is_valid():
        ser = AddressSerializer(data = data)
        ser.is_valid()
        print(ser.errors)
        return JsonResponse({'detail' : 'Invalid address.'}, status = 400)
    addr = Address(**data)
    addr.save()
    with GeographicInterface() as inter:
        latlng = inter.geocode(str(addr))
    if not latlng:
        return JsonResponse({'detail' : 'We couldn\'t geocode your address.'}, status = 400)
    location_data = {'latitude' : latlng[0], 'longitude' : latlng[1]}
    location = Location(**location_data)
    location.save()
    query = UserAddress.objects.filter(user = request.user)
    for item in query:
        item.delete()
    UserAddress(user = request.user, address = addr, location = location).save()
    query = Restaurant.objects.all()
    restaurant_list = []
    for restaurant in query:
        restaurant_list.append({'name' : restaurant.name, 'uuid' : restaurant.uuid})
    return JsonResponse(restaurant_list, safe = False)

class MenuSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required = True)

def menu(request):
    data = request.GET
    uuid = data.get('id')
    if not MenuSerializer(data = {'uuid' : uuid}).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    query = Restaurant.objects.filter(uuid = uuid)
    restaurant = query.first()
    if restaurant == None:
        return JsonResponse({'detail' : 'Restaurant with specified ID does not exist.'}, status = 400)
    menu = restaurant.menu
    query = MenuItem.objects.filter(menu = menu)
    item_list = []
    for item in query:
        item_list.append({'name' : item.name, 'description' : item.description, 'price' : item.price, 'uuid' : item.uuid})
    return JsonResponse(item_list, safe = False)

