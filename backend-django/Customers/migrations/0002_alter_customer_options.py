# Generated by Django 5.0.6 on 2024-06-07 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': (('change_customer_details_on_appointment_form', 'Can change customer details on appointment form'),)},
        ),
    ]