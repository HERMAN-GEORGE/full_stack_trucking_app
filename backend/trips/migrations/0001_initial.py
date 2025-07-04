# Generated by Django 4.2.23 on 2025-06-28 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_location', models.CharField(max_length=255)),
                ('pickup_location', models.CharField(max_length=255)),
                ('dropoff_location', models.CharField(max_length=255)),
                ('current_cycle_used_hrs', models.DecimalField(decimal_places=2, max_digits=5)),
                ('route_distance_miles', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('route_duration_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('route_geojson', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
