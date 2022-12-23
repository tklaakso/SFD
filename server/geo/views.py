from django.shortcuts import render
from django.http import JsonResponse

from .models import UserAddress

def address(request):
    query = UserAddress.objects.filter(user = request.user)
    addr = query.first()
    if not addr:
        return JsonResponse({'detail' : 'You do not have an active address.'}, status = 400)
    addr_obj = {'street_num' : addr.address.street_num,
                'street_name' : addr.address.street_name,
                'city' : addr.address.city,
                'province' : addr.address.province,
                'postal_code' : addr.address.postal_code,
                'country' : addr.address.country,
                'unit' : addr.address.unit  }
    return JsonResponse(addr_obj)
