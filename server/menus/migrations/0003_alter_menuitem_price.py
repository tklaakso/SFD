# Generated by Django 4.1.3 on 2022-12-24 13:12

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("menus", "0002_menuitem_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitem",
            name="price",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=10
            ),
        ),
    ]
