from django.contrib import admin
from django.conf import settings
# from django.contrib.auth import get_user_model
from .models import Appointment, Note

# User = get_user_model()

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    readonly_fields = ('user',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm('appointments.view_note'):
            return qs
        # if request.user.has_perm('appointments.change_note'):
        #     return qs.filter(user=request.user)
        # if request.user.has_perm('appointments.delete_note'):
        #     return qs
        # if request.user.has_perm('appointments.add_note'):
        #     return qs
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('appointments.change_note'):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('appointments.delete_note'):
            return True
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        if request.user.has_perm('appointments.add_note'):
            return True
        return super().has_add_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.has_perm('appointments.view_note'):
            return True
        return super().has_add_permission(request, obj)

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if obj else 0  # To avoid adding extra forms on a new object

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = settings.AUTH_USER_MODEL.objects.filter(pk=request.user.pk)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_formset(self, request, form, formset, change):
        if formset.model == Note:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.user_id:
                    instance.user = request.user
                instance.save()
            formset.save_m2m()
        else:
            formset.save()

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'appointment_id', 'created_at', 'user_phone_agent', 'user_field_agent', 
        'customer', 'scheduled', 'complete', 'disposition_id'
    )
    list_filter = ('scheduled', 'complete', 'customer')
    search_fields = (
        'appointment_id', 'customer__name', 'user_phone_agent__username', 
        'user_field_agent__username', 'disposition_id'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    inlines = [NoteInline]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == Note:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.user_id:
                    instance.user = request.user
                instance.save()
            formset.save_m2m()
        else:
            formset.save()