# Generated by Django 4.1.3 on 2022-12-23 20:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_cartmenuitemquantity_ordermenuitemquantity_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_time",
            field=models.DateTimeField(
                default=datetime.datetime.now, verbose_name="order time"
            ),
        ),
    ]
