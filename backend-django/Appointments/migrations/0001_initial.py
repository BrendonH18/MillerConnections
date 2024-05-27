# Generated by Django 5.0.6 on 2024-05-24 19:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appointment_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('scheduled', models.DateTimeField()),
                ('complete', models.DateTimeField(blank=True, null=True)),
                ('disposition_id', models.IntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Customers.customer')),
                ('user_field_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_agent', to=settings.AUTH_USER_MODEL)),
                ('user_phone_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_agent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]