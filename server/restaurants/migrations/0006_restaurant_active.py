# Generated by Django 4.1.3 on 2023-01-25 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0005_restaurant_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
