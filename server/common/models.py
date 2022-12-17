from django.db import models

class Address(models.Model):
    street_name = models.CharField('street name', max_length = 50)
    street_num = models.IntegerField('street number')
    city = models.CharField('city', max_length = 50)
    province = models.CharField('province', max_length = 30)
    postal_code = models.CharField('postal code', max_length = 6)