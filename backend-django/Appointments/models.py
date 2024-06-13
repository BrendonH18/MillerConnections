from django.db import models
from Customers.models import Customer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model() 

class Disposition(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )

class Contract(models.Model):
    def limit_field_agent_choices():
        return Q(groups__name='Field')

    name = models.CharField(max_length=255)
    receivable = models.DecimalField(max_digits=10, decimal_places=2)
    payable = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_eligible = models.BooleanField(default=False)
    # bonus_calculation = models.TextField(blank=True)  # Can store function logic as string or script
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    users = models.ManyToManyField(User, limit_choices_to=limit_field_agent_choices, related_name='contracts')

    def __str__(self):
        return self.name

    def is_active(self):
        return self.start_date <= timezone.now() <= self.end_date
    
    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )

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
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
            ("change_all_appointment_details", "Can change all appointment details"),
        )

    def __str__(self):
        return f"Appointment for {self.customer.name} on {self.scheduled.strftime('%m/%d/%Y')}"

   

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