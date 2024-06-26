from django.db import models
from django.utils import timezone

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

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    HOUR_CHOICES = [(i, f'{i}:00') for i in range(6, 22)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    hour = models.IntegerField(choices=HOUR_CHOICES)  # 24-hour format
    is_weekly_default = models.BooleanField(default=False, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_time_slots')
    source = models.CharField(max_length=10, choices=[('user', 'User'), ('system', 'System')], default='user')
    territory = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True, related_name='time_slots')

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