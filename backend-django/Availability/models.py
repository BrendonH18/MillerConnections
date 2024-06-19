from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeSlot(models.Model):
    HOUR_CHOICES = [(i, f'{i}:00') for i in range(6, 22)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    hour = models.IntegerField(choices=HOUR_CHOICES)  # 24-hour format
    is_weekly_default = models.BooleanField(default=False, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_time_slots')
    source = models.CharField(max_length=10, choices=[('user', 'User'), ('system', 'System')], default='user')

    class Meta:
        unique_together = ('user', 'date', 'hour')
        ordering = ['user', 'date', 'hour']
        verbose_name = 'TimeSlot'
        verbose_name_plural = 'TimeSlots'

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
