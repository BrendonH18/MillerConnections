from django.db import models
from django.utils import timezone
import datetime

from django.contrib.auth import get_user_model
User = get_user_model()

class Territory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='territories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Default is True
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        # Override the delete method to perform a soft delete
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['user', 'name']
        verbose_name = 'Territory'
        verbose_name_plural = 'Territories'
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )

    def __str__(self):
        return self.name

    
class Date(models.Model):
    HOUR_CHOICES = list(range(7, 22))
    date = models.DateField()
    status = models.CharField(max_length=255)
    territory = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True, related_name='territories')

    @property
    def week_of_month(self):
        first_day = self.date.replace(day=1)
        first_sunday = first_day + datetime.timedelta(days=(6 - first_day.weekday())) if first_day.weekday() != 6 else first_day
        return 1 if self.date < first_sunday else (self.date - first_sunday).days // 7 + 2

    @property
    def day_of_week(self):
        return (self.date.weekday() + 1) % 7 + 1
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_slots()

    def create_slots(self):
        for hour in self.HOUR_CHOICES:
            Slot.objects.get_or_create(date=self, start_time=datetime.time(hour=hour))

    def __str__(self):
        return f"Date: {self.date}, Week of Month: {self.week_of_month}, Day of Week: {self.day_of_week}"


class Slot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ]
    STATUS_DEFAULT = 'unavailable'
    SOURCE_CHOICES = [
        ('user', 'User'),
        ('pending', 'Pending'),
        ('recurring', 'Recurring'), 
        ('settings', 'Settings')
        ]
    SOURCE_DEFAULT = 'user'
    date = models.ForeignKey(Date, on_delete=models.CASCADE, related_name='slots')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_DEFAULT)
    start_time = models.TimeField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_DEFAULT)
    invitees_allowed = models.IntegerField(default=1)

    @property
    def invitees_remaining(self):
        remaining = self.invitees_allowed - self.appointments.count()
        self.update_status_based_on_remaining(remaining)
        return remaining
    
    def update_status_based_on_remaining(self, remaining):
        if remaining == 0:
            self.status = 'unavailable'
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Date: {self.date}, Hour: {self.start_time}"



class TimeSlot(models.Model):
    HOUR_CHOICES = [(i, f'{i}:00') for i in range(7, 22)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    hour = models.IntegerField(choices=HOUR_CHOICES)  # 24-hour format
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_time_slots')
    # User: a person
    # Pending: no interactions yet
    # Recurring: Built from "Settings"
    # Settings: Used to build "Recurring" at regular intervals. 
    source = models.CharField(max_length=10, choices=[('user', 'User'), ('pending', 'Pending'), ('recurring', 'Recurring'), ('settings', 'Settings')], default='user')
    territory = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True, related_name='time_slots')

    def weekday(self):
        return self.date.strftime('%A')

    weekday.short_description = 'Weekday'

    def save(self, *args, **kwargs):
        if not self.territory:
            default_territory, created = Territory.objects.get_or_create(
                user=self.user,
                name="Default",
                defaults={
                    'description': "Placeholder",
                    'is_active': False,
                    'created_at': timezone.now(),
                    'deleted_at': timezone.now(),
                    'is_default': True
                }
            )
            self.territory = default_territory
        super(TimeSlot, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'date', 'hour')
        ordering = ['user', 'date', 'hour']
        verbose_name = 'TimeSlot'
        verbose_name_plural = 'TimeSlots'
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )

    @classmethod
    def create_default_weekly_slots(cls, user, start_date, end_date, hour):
        from datetime import timedelta
        current_date = start_date
        slots = []
        while current_date <= end_date:
            slots.append(cls(user=user, date=current_date, hour=hour, is_weekly_default=True))
            current_date += timedelta(weeks=1)
        cls.objects.bulk_create(slots)

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.hour}:00'