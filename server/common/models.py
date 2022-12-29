from django.db import models

class Address(models.Model):
    street_name = models.CharField('street name', max_length = 50)
    street_num = models.CharField('street number', max_length = 10)
    city = models.CharField('city', max_length = 50)
    province = models.CharField('province', max_length = 30)
    postal_code = models.CharField('postal code', max_length = 10)
    country = models.CharField('country', max_length = 30, default = 'Canada')
    unit = models.CharField('unit', max_length = 100, default = '', blank = True)

    def serialize(self):
        return {
            'street_name' : self.street_name,
            'street_num' : self.street_num,
            'city' : self.city,
            'province' : self.province,
            'postal_code' : self.postal_code,
            'country' : self.country,
            'unit' : self.unit,
        }
    
    def __str__(self):
        return str(self.street_num) + ' ' + str(self.street_name) + ', ' + str(self.city) + ', ' + str(self.province) + ', ' + str(self.country) + ', ' + str(self.postal_code)