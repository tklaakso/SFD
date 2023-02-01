# Generated by Django 4.1.3 on 2023-01-29 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("driver", "0006_alter_driverorder_order"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="driver",
            name="accepted",
        ),
        migrations.RemoveField(
            model_name="driver",
            name="declined",
        ),
        migrations.RemoveField(
            model_name="driver",
            name="recommended",
        ),
        migrations.AddField(
            model_name="driverorder",
            name="driver_accepted",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accepted",
                to="driver.driver",
            ),
        ),
        migrations.AddField(
            model_name="driverorder",
            name="driver_declined",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="declined",
                to="driver.driver",
            ),
        ),
        migrations.AddField(
            model_name="driverorder",
            name="driver_recommended",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recommended",
                to="driver.driver",
            ),
        ),
    ]
