# Generated by Django 4.1.3 on 2022-12-27 18:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orders", "0007_order_address"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Driver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "accepted",
                    models.ManyToManyField(
                        related_name="driver_accepted", to="orders.order"
                    ),
                ),
                (
                    "declined",
                    models.ManyToManyField(
                        related_name="driver_declined", to="orders.order"
                    ),
                ),
                (
                    "recommended",
                    models.ManyToManyField(
                        related_name="driver_recommended", to="orders.order"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
