# Generated by Django 4.1.3 on 2022-12-04 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0001_initial"),
        ("restaurants", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="common.address",
            ),
        ),
    ]
