from django import forms
from django_select2.forms import Select2Widget
from .models import TimeSlot, Territory
from bootstrap_datepicker_plus.widgets import DatePickerInput


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
        fields = ['user', 'date', 'territory']
        widgets = {
            'date': DatePickerInput(options={'inline': True, 'keepOpen': True}),
        }
    class Media:
        js = ('availability/update_hourly_availability_given_day_and_user.js',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.setup_select2('territory', Territory.objects.filter(user=user, is_active=True) if user else None, not user, "Select a user first to choose a territory.")

class TerritoryForm(forms.ModelForm):
    class Meta:
        model = Territory
        fields = ['name', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_select2('user')


class TimeSlotChangeForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = '__all__'  # Include all fields from the TimeSlot model