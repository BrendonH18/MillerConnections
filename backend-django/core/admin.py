from django.contrib import admin
from Users.models import Supervision

class CustomModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.user_permissions.filter(
            content_type__model=self.model._meta.model_name,
            codename='show_on_admin_dashboard'
        ).exists()
    
    def get_all_supervised_users(self, user):
        supervised_users = set(Supervision.objects.filter(supervisor=user).values_list('supervised', flat=True))
        all_supervised_users = set(supervised_users)

        while supervised_users:
            new_supervised_users = set(Supervision.objects.filter(supervisor__in=supervised_users).values_list('supervised', flat=True))
            supervised_users = new_supervised_users - all_supervised_users
            all_supervised_users.update(supervised_users)

        return all_supervised_users
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        all_supervised_users = self.get_all_supervised_users(request.user)
        request.all_supervised_users = all_supervised_users
        return qs