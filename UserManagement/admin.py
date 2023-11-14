from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
       
    list_display = (
        'name', 
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
                        'first_name',
                        'last_name',
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