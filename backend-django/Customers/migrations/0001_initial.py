# Generated by Django 5.0.6 on 2024-05-24 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('phone1', models.IntegerField()),
                ('phone2', models.IntegerField(blank=True, null=True)),
                ('street', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('complete', models.CharField(max_length=255)),
                ('zip', models.CharField(max_length=10)),
            ],
        ),
    ]