from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    phone_number = PhoneNumberField(region="US", blank=False, null=False, unique=True)
    def __str__(self) -> str:
        return self.get_full_name()