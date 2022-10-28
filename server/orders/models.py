from django.db import models

class Order(models.Model):
    placement_date = models.DateTimeField('time placed')