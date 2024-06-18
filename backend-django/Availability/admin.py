from django.contrib import admin
from .models import TimeSlot
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hour', 'is_available')
    list_filter = ('user', 'date', 'hour', 'is_available')
    search_fields = ('user__username', 'date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Field').exists():
            return qs.filter(user=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['user']
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['availabilities'] = TimeSlot.objects.all()
        return super(TimeSlotAdmin, self).changelist_view(request, extra_context=extra_context)

# admin.site.register(TimeSlot, TimeSlotAdmin)
