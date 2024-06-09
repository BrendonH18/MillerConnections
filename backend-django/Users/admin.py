from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.models import Group

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.user_permissions.filter(content_type__model=self.model.__name__.lower(), codename='show_on_admin_dashboard').exists()
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display: tuple[str] = ("full_name", "is_staff", "is_active",)
    list_filter: tuple[str] = ("is_staff", "is_active",)
    fieldsets: tuple = (
        (None, {"fields": ("email", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets: tuple = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "first_name","last_name", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields: tuple = ("email","first_name", "last_name")
    ordering: tuple[str] = ( "first_name",)

    @admin.display(empty_value="N/A", description="Name", ordering="first_name")
    def full_name(self, object):
        return f"{object.first_name} {object.last_name}".title()

admin.site.unregister(Group)

class CustomGroup(Group):
    class Meta:
        proxy = True 
        permissions = (
            ("show_on_admin_dashboard", "Show on Admin Dashboard"),
        )
        verbose_name = "Group"
        verbose_name_plural = "Groups"
    

class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.user_permissions.filter(content_type__model=self.model.__name__.lower(), codename='show_on_admin_dashboard').exists()
admin.site.register(CustomGroup, GroupAdmin)