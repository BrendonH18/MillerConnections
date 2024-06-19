from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeSlot(models.Model):
    HOUR_CHOICES = [(i, f'{i}:00') for i in range(6, 22)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()   
    hour = models.IntegerField(choices=HOUR_CHOICES)  # 24-hour format

    class Meta:
        unique_together = ('user', 'date', 'hour')

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.hour}:00'
