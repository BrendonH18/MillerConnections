from django.db import models
from Customers.models import Customer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model() 

class Disposition(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )
    
# class ChangeLog(models.Model):
#     appointment = models.ForeignKey('Appointment', related_name='changes', on_delete=models.CASCADE)
#     changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     change_timestamp = models.DateTimeField(default=timezone.now)
#     changes = models.TextField()

#     def __str__(self):
#         return f"Change by {self.changed_by} on {self.change_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Appointment(models.Model):
    def get_default_disposition():
        disposition, created = Disposition.objects.get_or_create(name="Disposition Needed")
        return disposition.id
    
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
    disposition = models.ForeignKey(
        Disposition, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        default=get_default_disposition
    )
    recording = models.TextField(default='', blank=True)

    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
            ("change_all_appointment_details", "Can change all appointment details"),
        )

    def __str__(self):
        return f"Appointment for {self.customer.name} on {self.scheduled.strftime('%m/%d/%Y')}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If the object already exists, it's an update
            original = Appointment.objects.get(pk=self.pk)
            changes = []
            for field in self._meta.fields:
                field_name = field.name
                original_value = getattr(original, field_name)
                new_value = getattr(self, field_name)
                if original_value != new_value:
                    changes.append(f"{field.verbose_name}: {original_value} -> {new_value}")
            # if changes:
            #     ChangeLog.objects.create(
            #         appointment=self,
            #         changed_by=self.user,  # Assuming the user_phone_agent is the one making changes
            #         changes='\n'.join(changes)
            #     )
        super().save(*args, **kwargs)

   

class Note(models.Model):
    appointment = models.ForeignKey(Appointment, related_name='notes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.user} on {self.appointment}"
    
    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )