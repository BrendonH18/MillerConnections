# Generated by Django 5.0.6 on 2024-06-09 00:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_customgroup_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customgroup',
            options={'permissions': (('show_on_admin_dashboard', 'Show on Admin Dashboard'),), 'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': (('show_on_admin_dashboard', 'Show on Admin Dashboard'),), 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.CreateModel(
            name='Supervision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('supervised', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervised_set', to=settings.AUTH_USER_MODEL)),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Supervision',
                'verbose_name_plural': 'Supervisions',
                'permissions': (('show_on_admin_dashboard', 'Show on Admin Dashboard'),),
            },
        ),
        migrations.AddConstraint(
            model_name='supervision',
            constraint=models.UniqueConstraint(fields=('supervisor', 'supervised'), name='unique_supervisor_supervised'),
        ),
    ]
