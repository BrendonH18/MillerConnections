# Generated by Django 5.0.6 on 2024-06-08 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0006_appointment_recording'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appointment',
            options={'permissions': (('show_on_admin_dashboard', 'Show on Admin Dashboard'), ('change_all_appointment_details', 'Can change all appointment details'))},
        ),
    ]
