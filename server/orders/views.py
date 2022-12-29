from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from menus.models import MenuItem
from financial.utils import calculate_price
from geo.models import UserAddress
from .models import CartMenuItemQuantity, OrderMenuItemQuantity, Cart, Order
from driver.selection import on_place_order

import json

from rest_framework import serializers

def get_cart(request):
    if not Cart.objects.filter(owner = request.user).first():
        cart = Cart(owner = request.user)
        cart.save()
    return request.user.cart

class AddFormSerializer(serializers.Serializer):
    item = serializers.UUIDField(required = True)
    quantity = serializers.IntegerField(required = True, max_value = 1000)

def add(request):
    cart = get_cart(request)
    data = json.loads(request.body)
    if not AddFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    item_id = data.get('item')
    quantity = data.get('quantity')
    item = MenuItem.objects.filter(uuid = item_id).first()
    if not item:
        return JsonResponse({'detail' : 'No menu item exists with specified ID.'}, status = 400)
    if quantity <= 0:
        return JsonResponse({'detail' : 'Quantity must be positive.'}, status = 400)
    for current_item in cart.items():
        if current_item.item == item:
            current_item.quantity += quantity
            current_item.save()
            return JsonResponse({'detail' : 'Successfully added item.'})
    item_quantity = CartMenuItemQuantity(item = item, quantity = quantity, cart = cart)
    item_quantity.save()
    return JsonResponse({'detail' : 'Successfully added item.'})

class RemoveFormSerializer(serializers.Serializer):
    item = serializers.UUIDField(required = True)

def remove(request):
    cart = get_cart(request)
    data = json.loads(request.body)
    if not RemoveFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    item = data.get('item')
    if not MenuItem.objects.filter(uuid = item).first():
        return JsonResponse({'detail' : 'No menu item exists with specified ID.'}, status = 400)
    to_remove = None
    for item_quantity in cart.items():
        if item_quantity.uuid == item:
            to_remove = item_quantity
            break
    if not to_remove:
        return JsonResponse({'detail' : 'Item with specified ID does not exist in your cart.'}, status = 400)
    to_remove.delete()
    return JsonResponse({'detail' : 'Item removed successfully.'})

def cart(request):
    cart = get_cart(request)
    item_list = []
    for item in cart.items():
        item_list.append({'uuid' : item.uuid, 'name' : item.item.name, 'quantity' : item.quantity})
    return JsonResponse(item_list, safe = False)

class PlaceFormSerializer(serializers.Serializer):
    time = serializers.DateTimeField(required = True)

def place(request):
    data = json.loads(request.body)
    if not PlaceFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    time = data.get('time')
    cart = get_cart(request)
    items = cart.items()
    if items.count() == 0:
        return JsonResponse({'detail' : 'Cannot place order with empty cart.'}, status = 400)
    restaurants = list({item.item.menu.restaurant for item in items})
    price = calculate_price(items)
    address = UserAddress.objects.filter(user = request.user).first()
    if not address:
        return JsonResponse({'detail' : 'You do not have an active delivery address.'}, status = 400)
    order = Order(order_time = time, owner = request.user, price = price, address = address.address, location = address.location)
    order.save()
    for restaurant in restaurants:
        order.restaurants.add(restaurant)
    order.save()
    for item in items:
        order_item = OrderMenuItemQuantity(order = order, item = item.item, quantity = item.quantity)
        order_item.save()
        item.delete()
    on_place_order(order)
    return JsonResponse({'detail' : 'Successfully placed order.'})

class CancelFormSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required = True)

def cancel(request):
    data = json.loads(request.body)
    if not CancelFormSerializer(data = data).is_valid():
        return JsonResponse({'detail' : 'Validation failed.'}, status = 400)
    uuid = data.get('uuid')
    order = Order.objects.filter(uuid = uuid, owner = request.user).first()
    if not order:
        return JsonResponse({'detail' : 'Order with specified UUID does not exist.'}, status = 400)
    order.delete()
    return JsonResponse({'detail' : 'Successfully cancelled order.'})

def view_all(request):
    query = Order.objects.filter(owner = request.user)
    order_list = []
    for order in query:
        order_list.append({'uuid' : order.uuid, 'time' : order.order_time, 'restaurants' : [restaurant.name for restaurant in order.restaurants.all()], 'price' : order.price, 'address' : order.address.serialize()})
    return JsonResponse(order_list, safe = False)
