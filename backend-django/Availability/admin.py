from django.contrib import admin
from .models import TimeSlot, Territory
from .forms import TimeSlotAddForm, TimeSlotChangeForm
from django.contrib.auth import get_user_model
from core.admin import CustomModelAdmin
from django.db.models import Q
from .forms import TerritoryForm
from django.urls import resolve

User = get_user_model()

@admin.register(TimeSlot)
class TimeSlotAdmin(CustomModelAdmin):
    list_display = ('user', 'date', 'hour', 'territory', 'created_by', 'source')
    list_filter = ('user', 'date', 'hour', 'territory')
    search_fields = ('user', 'date', 'territory')

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            # self.form = TimeSlotAddForm  # Use your specific form for adding
            custom_kwargs = kwargs
            custom_kwargs['request'] = request
            custom_kwargs['all_supervised_users'] = self.get_all_supervised_users(request.user) 
            form_class = TimeSlotAddForm
            class FormWithRequest(form_class):
                def __init__(self, *args, **form_kwargs):
                    form_kwargs.update(custom_kwargs)  # Add custom arguments back
                    super().__init__(*args, **form_kwargs)

            return FormWithRequest
        else:
            custom_kwargs = kwargs
            custom_kwargs['request'] = request
            custom_kwargs['all_supervised_users'] = self.get_all_supervised_users(request.user) 
            form_class = TimeSlotChangeForm
            class FormWithRequest(form_class):
                def __init__(self, *args, **form_kwargs):
                    form_kwargs.update(custom_kwargs)  # Add custom arguments back
                    super().__init__(*args, **form_kwargs)

            return FormWithRequest
        return super(TimeSlotAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        resolver_match = resolve(request.path_info)
        if resolver_match.url_name == 'Availability_timeslot_changelist':
            qs = super().get_queryset(request)
            if request.user.is_superuser:
                return qs
            all_supervised_users = self.get_all_supervised_users(request.user)
            return qs.filter(Q(user=request.user) | Q(user__in=all_supervised_users))
        else:
            return super().get_queryset(request)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['availabilities'] = TimeSlot.objects.all()
        return super(TimeSlotAdmin, self).changelist_view(request, extra_context=extra_context)

@admin.register(Territory)
class TerritoryAdmin(CustomModelAdmin):
    list_display = ('name', 'user', 'description', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ('name', 'user__username')
    actions = ['make_active', 'make_inactive']

    readonly_fields = ('created_at', 'deleted_at', 'is_default')

    form = TerritoryForm

    def get_form(self, request, obj=None, **kwargs):
        custom_kwargs = {}
        custom_kwargs['request'] = request
        custom_kwargs['all_supervised_users'] = self.get_all_supervised_users(request.user) 
        form_class = super().get_form(request, obj, **kwargs)
        class FormWithRequest(form_class):
            def __init__(self, *args, **form_kwargs):
                form_kwargs.update(custom_kwargs)  # Add custom arguments back
                super().__init__(*args, **form_kwargs)

        return FormWithRequest
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        all_supervised_users = self.get_all_supervised_users(request.user)
        return qs.filter(Q(user=request.user, is_active=True) | Q(user__in=all_supervised_users, is_active=True))
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected territories as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected territories as inactive"