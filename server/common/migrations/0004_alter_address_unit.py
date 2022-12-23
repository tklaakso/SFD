# Generated by Django 4.1.3 on 2022-12-23 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0003_alter_address_postal_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="unit",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="unit"
            ),
        ),
    ]
