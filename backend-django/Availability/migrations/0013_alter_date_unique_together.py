# Generated by Django 5.0.6 on 2024-07-12 21:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Availability', '0012_slot_update_appointment_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='date',
            unique_together={('date', 'user')},
        ),
    ]