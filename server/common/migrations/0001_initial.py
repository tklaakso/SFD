# Generated by Django 4.1.3 on 2022-12-04 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
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
                    "street_name",
                    models.CharField(max_length=50, verbose_name="street name"),
                ),
                ("street_num", models.IntegerField(verbose_name="street number")),
                ("city", models.CharField(max_length=50, verbose_name="city")),
                ("province", models.CharField(max_length=30, verbose_name="province")),
                (
                    "postal_code",
                    models.CharField(max_length=6, verbose_name="postal code"),
                ),
            ],
        ),
    ]
