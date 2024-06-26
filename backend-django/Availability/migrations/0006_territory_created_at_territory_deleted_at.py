# Generated by Django 5.0.6 on 2024-06-26 19:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Availability', '0005_territory_timeslot_territory'),
    ]

    operations = [
        migrations.AddField(
            model_name='territory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='territory',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
