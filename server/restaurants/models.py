from django.db import models
from django.contrib.auth.models import User
from common.models import Address

class Restaurant(models.Model):
    name = models.CharField('name', max_length = 100)
    address = models.ForeignKey(Address, on_delete = models.CASCADE, blank = True, null = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)