from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    hour = models.IntegerField(choices=[(i, f'{i}:00') for i in range(24)])  # 24-hour format
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'date', 'hour')

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.hour}:00'
