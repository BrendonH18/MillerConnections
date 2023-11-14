from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# from .forms import CustomUserChangeForm, CustomUserCreationForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    # model = CustomUser
    list_display = (
        'email', 
        "is_staff", 
        "is_active",
        )
    search_fields = (
        'email',
        )
    ordering = (
        "email",
        )
    add_fieldsets = (
            (
                None,
                {
                    'classes': (
                        'wide',
                        ),
                    'fields': (
                        'email', 
                        'username', 
                        'password1', 
                        'password2'
                        ),
                },
            ),
        )
    

# admin.site.register(CustomUser, CustomUserAdmin)