from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint

from .managers import CustomUserManager

class CustomUser(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    avatar = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["first_name", "last_name"]

    objects = CustomUserManager()
    class Meta:
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )
        verbose_name: str = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.get_full_name()
    
class Supervision(models.Model):
    supervisor = models.ForeignKey(CustomUser, related_name='supervisor_set', on_delete=models.CASCADE)
    supervised = models.ForeignKey(CustomUser, related_name='supervised_set', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['supervisor', 'supervised'], name='unique_supervisor_supervised')
        ]
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )
        verbose_name = 'Supervision'
        verbose_name_plural = 'Supervisions'