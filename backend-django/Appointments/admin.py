from django.contrib import admin
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import Appointment, Note, Disposition, Contract
from .forms import AppointmentForm, ReadOnlyAppointmentForm
from django.utils.html import format_html
from core.admin_custom  import CustomAdminSite
from Users.models import Supervision
from django.db.models import Q
from core.admin import CustomModelAdmin


# Field Agent cost varies between 125 - 200
# Phone Agent get bonuses based on volume. Every 10 installs from 175 tier and up they get a bonus. Otherwise 50.

# Contract: (One or More per Field Rep)
# name = "Fiber First"
# receivable = 250
# payable = 100
# bonus_eligible = False
# bonus_calculation = 

# Authentication FrontEnd

User = get_user_model()
custom_admin_site = CustomAdminSite(name="custom_admin")
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
class AppointmentAdmin(CustomModelAdmin):
    list_display = (
        'appointment_id', 'created_at', 'user_phone_agent', 'user_field_agent',
        'customer', 'scheduled', 'complete', 'disposition_id',
    )
    list_filter = ('scheduled', 'complete', 'customer')
    search_fields = (
        'appointment_id', 'customer__name', 'user_phone_agent__username',
        'user_field_agent__username', 'disposition_id'
    )
    ordering = ('-created_at',)
    # readonly_fields = ('created_at',)

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone1', 'customer_phone2', 'customer_street', 'customer_state', 'customer_zip')
        }),
        ('Appointment Information', {
            'fields': ('user_field_agent','user_phone_agent','scheduled', 'complete', 'disposition', 'recording','contract')
        }),
    )

    inlines = [NoteInline]

    class Media:
        js = ('appointments/update_contract_given_field_agent.js',)

    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        all_supervised_users = self.get_all_supervised_users(request.user)
        # Get all supervised users recursively
        if request.user.groups.filter(name='Field').exists():
            # Filter appointments for the logged-in user or supervised users
            return qs.filter(Q(user_field_agent=request.user) | Q(user_field_agent__in=all_supervised_users))
        if request.user.groups.filter(name='Phone').exists():
            # Filter appointments for the logged-in user or supervised users
            return qs.filter(Q(user_phone_agent=request.user) | Q(user_phone_agent__in=all_supervised_users))
        else:
            return qs.none()

    def save_model(self, request, obj, form, change):
        form.save(commit=True, user=request.user)
        super().save_model(request, obj, form, change)

    form = AppointmentForm
    def get_form(self, request, obj=None, **kwargs):
            custom_kwargs = {}
            custom_kwargs['request'] = request
            form_class = super().get_form(request, obj, **kwargs)
            class FormWithRequest(form_class):
                def __init__(self, *args, **form_kwargs):
                    form_kwargs.update(custom_kwargs)  # Add custom arguments back
                    super().__init__(*args, **form_kwargs)

            return FormWithRequest

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
class DispositionAdmin(CustomModelAdmin):
    list_display = ('name',)  # This tuple specifies the fields to display in the admin list view
    search_fields = ('name',)  # This enables a search box that searches the 'name' field

@admin.register(Contract)
class ContractAdmin(CustomModelAdmin):
    list_display = ('name', 'receivable', 'payable', 'bonus_eligible', 'start_date', 'end_date', 'created_at')
    list_filter = ('bonus_eligible', 'start_date', 'end_date')
    search_fields = ('name', 'users__email', 'users__first_name', 'users__last_name')
    filter_horizontal = ('users',)

    fieldsets = (
        (None, {
            'fields': ('name', 'receivable', 'payable', 'bonus_eligible', 'start_date', 'end_date', 'users')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['name', 'receivable', 'payable', 'bonus_eligible', 'start_date', 'end_date', 'users']
        return []