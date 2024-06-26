from django.contrib import admin
from .models import TimeSlot, Territory
from .forms import TimeSlotAddForm, TimeSlotChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hour', 'territory', 'created_by', 'source')
    list_filter = ('user', 'date', 'hour', 'territory')
    search_fields = ('user', 'date', 'territory')

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.form = TimeSlotAddForm  # Use your specific form for adding
        else:
            self.form = TimeSlotChangeForm  # Use your specific form for changing
        return super(TimeSlotAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.all()
        return qs.filter(user=request.user)

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

@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ('name', 'user__username')
    actions = ['make_active', 'make_inactive']

    readonly_fields = ('created_at', 'deleted_at', 'is_default')

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected territories as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected territories as inactive"