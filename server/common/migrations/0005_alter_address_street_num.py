# Generated by Django 4.1.3 on 2022-12-28 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0004_alter_address_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="street_num",
            field=models.CharField(max_length=10, verbose_name="street number"),
        ),
    ]
