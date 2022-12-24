from decimal import *

def calculate_price(items):
    price = Decimal('0')
    for item in items:
        price += Decimal(str(item.item.price)) * Decimal(str(item.quantity))
    return float(price)
