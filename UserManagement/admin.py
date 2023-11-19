from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from phonenumber_field.formfields import PhoneNumberField

class PhoneForm(forms.Form):
    number = PhoneNumberField(region="US")

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
       
    list_display = (
        'name',
        'is_staff', 
        'is_active',
        )
    search_fields = (
        'email',
        )
    ordering = (
        "email",
        )
    fieldsets = (
        (None, {
            "fields": (
                'username',
            ),
        }),
        (_('Personal Information'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone_number'
            ),
        }),
        (_('Permissions'), {
            'fields': (
                'password',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        })
    )
    
    add_fieldsets = (
            (
                None,
                {
                    'classes': (
                        'wide',
                        ),
                    'fields': (
                        'first_name',
                        'last_name',
                        'phone_number',
                        'email', 
                        'username', 
                        'password1', 
                        'password2'
                        ),
                },
            ),
        )

    def name(self, user):
        return user.get_full_name()
    
    


# admin.site.register(CustomUser, CustomUserAdmin)