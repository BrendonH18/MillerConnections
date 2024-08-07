# Generated by Django 5.0.6 on 2024-07-03 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointments', '0010_alter_contract_users'),
        ('Availability', '0010_date_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='slots',
            field=models.ManyToManyField(related_name='appointment_slots', to='Availability.slot'),
        ),
        migrations.AddField(
            model_name='contract',
            name='slots',
            field=models.ManyToManyField(related_name='appointments', to='Availability.slot'),
        ),
    ]
