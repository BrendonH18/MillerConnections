from django.contrib import admin
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import Appointment, Note, Disposition

User = get_user_model()
app_label = apps.get_app_config('Appointments').label

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    readonly_fields = ('user',)

    def get_queryset(self, request):
        qs = super(NoteInline, self).get_queryset(request)
        if request.user.has_perm(f'{app_label}.view_note'):
            return qs
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm(f'{app_label}.change_note'):
            return True
        return super(NoteInline, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm(f'{app_label}.delete_note'):
            return True
        return super(NoteInline, self).has_delete_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        # return request.user.has_perm(f'{app_label}.add_note') or super(NoteInline, self).has_add_permission(request, obj)
        if request.user.has_perm(f'{app_label}.add_note'):
            return True
        return super(NoteInline, self).has_add_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        if request.user.has_perm(f'{app_label}.view_note'):
            return True
        return super(NoteInline, self).has_view_permission(request, obj)

    def get_extra(self, request, obj=None, **kwargs):
        return 1 if obj else 0  # To avoid adding extra forms on a new object

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
            return super(NoteInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        return super(NoteInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
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

@admin.register(Disposition)
class DispositionAdmin(admin.ModelAdmin):
    list_display = ('name',)  # This tuple specifies the fields to display in the admin list view
    search_fields = ('name',)  # This enables a search box that searches the 'name' field