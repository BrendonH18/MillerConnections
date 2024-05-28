from django.db import models
from Customers.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)  # INT IDENTITY
    created_at = models.DateTimeField(auto_now_add=True)  # DateTime
    user_phone_agent = models.ForeignKey(
        User,
        related_name='phone_agent',
        on_delete=models.CASCADE
    )  # ForeignKey to User model
    user_field_agent = models.ForeignKey(
        User,
        related_name='field_agent',
        on_delete=models.CASCADE
    )  # ForeignKey to User model
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # ForeignKey to Customer
    scheduled = models.DateTimeField()  # DateTime
    complete = models.DateTimeField(blank=True, null=True)  # DateTime, allowing it to be blank or null
    disposition_id = models.IntegerField(blank=True, null=True)  # INT

    def __str__(self):
        return f"Appointment for {self.customer.name} on {self.scheduled.strftime('%m/%d/%Y')}"


class Note(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='notes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.user} on {self.appointment}"