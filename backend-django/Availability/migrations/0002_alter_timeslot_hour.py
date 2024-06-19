# Generated by Django 5.0.6 on 2024-06-16 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Availability', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='hour',
            field=models.IntegerField(choices=[(6, '6:00'), (7, '7:00'), (8, '8:00'), (9, '9:00'), (10, '10:00'), (11, '11:00'), (12, '12:00'), (13, '13:00'), (14, '14:00'), (15, '15:00'), (16, '16:00'), (17, '17:00'), (18, '18:00'), (19, '19:00'), (20, '20:00'), (21, '21:00')]),
        ),
    ]