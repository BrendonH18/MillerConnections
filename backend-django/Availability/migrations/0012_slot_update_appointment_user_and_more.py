# Generated by Django 5.0.6 on 2024-07-12 20:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Availability', '0011_date_user_alter_date_territory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='slot',
            name='update_appointment_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_update_slots', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='slot',
            name='update_availability_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='availability_update_slots', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='slot',
            name='source',
            field=models.CharField(choices=[('user', 'User'), ('pending', 'Pending'), ('recurring', 'Recurring'), ('settings', 'Settings')], default='pending', max_length=10),
        ),
    ]
