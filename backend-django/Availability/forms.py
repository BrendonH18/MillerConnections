from django import forms
from django_select2.forms import Select2Widget
from .models import TimeSlot, Territory
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Select2Mixin:
    def setup_select2(self, field_name, queryset=None, disabled=False, help_text=None):
        self.fields[field_name].widget = Select2Widget()
        if queryset is not None:
            self.fields[field_name].queryset = queryset
        if disabled:
            self.fields[field_name].disabled = True
            self.fields[field_name].help_text = help_text   

class TimeSlotAddForm(Select2Mixin, forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['user', 'date']
        widgets = {
            'date': DatePickerInput(options={'inline': True, 'keepOpen': True}),
        }
    class Media:
        js = ('availability/update_hourly_availability_given_day_and_user.js',)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        all_supervised_users = kwargs.pop('all_supervised_users', None)
        change = kwargs.pop('change', None)
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)


        # self.setup_select2('territory', Territory.objects.filter(user=user, is_active=True) if user else None, not user, "Select a user first to choose a territory.")

class TerritoryForm(forms.ModelForm):
    class Meta:
        model = Territory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        all_supervised_users = kwargs.pop('all_supervised_users', None)
        super().__init__(*args, **kwargs)
        if request and request.user.is_superuser:
            pass
        else:
            if request and all_supervised_users is not None:
                queryset = User.objects.filter(
                    Q(id__in=all_supervised_users) | Q(id=request.user.id)
                )
                self.fields['user'].queryset = queryset
                if queryset.count() == 1:
                    self.fields['user'].initial = queryset.first()
                    self.fields['user'].disabled = True
        # self.setup_select2('user')


class TimeSlotChangeForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = '__all__'  # Include all fields from the TimeSlot model
  
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        all_supervised_users = kwargs.pop('all_supervised_users', None)
        change = kwargs.pop('change', None)
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        instance = kwargs.get('instance')
        if not request or not instance:
            return

        self._configure_user_field(instance)
        self._configure_created_by_field(instance)
        self._configure_source_field(request)
        self._configure_territory_field(instance, request)

    def _configure_user_field(self, instance):
        user_query = User.objects.filter(id=instance.user.pk)
        self.fields['user'].queryset = user_query
        self.fields['user'].initial = user_query.first()
        self.initial['user'] = instance.user.pk

    def _configure_created_by_field(self, instance):
        created_by_query = User.objects.filter(id=instance.created_by.pk)
        self.fields['created_by'].queryset = created_by_query
        self.fields['created_by'].initial = created_by_query.first()
        self.initial['created_by'] = created_by_query.first().pk

    def _configure_source_field(self, request):
        initial_source = self.fields['source'].initial
        if not request.user.is_superuser:
            self.fields['source'].choices = [(key, value) for key, value in self.fields['source'].choices if key == initial_source]

    def _configure_territory_field(self, instance, request):
        user = instance.user
        territory_query = Territory.objects.filter(
            Q(user=user, is_active=True) | Q(id=instance.territory.id) | Q(user=user, is_default=True)
        ) if instance.territory else Territory.objects.filter(
            Q(user=user, is_active=True) | Q(user=user, is_default=True)
        )

        if not territory_query:
            default_territory, _ = Territory.objects.get_or_create(
                user=user,
                is_default=True,
                defaults={'name': "Default", 'description': "Placeholder", 'is_active': False,
                          'created_at': timezone.now(), 'deleted_at': timezone.now()}
            )
            territory_query = Territory.objects.filter(id=default_territory.id)

        self.fields['territory'].queryset = territory_query
        self.fields['territory'].initial = territory_query.first()
        self.initial['territory'] = territory_query.first().pk

        if territory_query.count() == 1 or not request.user.is_superuser:
            self.fields['territory'].disabled = True

        if not request.user.is_superuser:
            for field_name in self.fields:
                if field_name != 'territory':
                    self.fields[field_name].disabled = True