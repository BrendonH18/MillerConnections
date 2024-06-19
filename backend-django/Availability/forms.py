from django import forms
# from django_flatpickr.widgets import DatePickerInput
# from django_flatpickr.schemas import FlatpickrOptions
from django_select2.forms import Select2Widget
from .models import TimeSlot
from bootstrap_datepicker_plus.widgets import DatePickerInput


class DateInput(forms.DateInput):
    input_type = 'date'

class JQueryDatePickerInput(DatePickerInput):
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.0.min.js','availability/update_hourly_availability_given_day_and_user.js')

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['user','date']
        widgets = {
            'date': JQueryDatePickerInput(options={
                # 'dayViewHeaderFormat': 'MMMM YYYY',
                'inline': True,
                'keepOpen': True,
                # 'collapse': False
                # 'showTodayButton': True
        }),
            # 'hour': Select2Widget(),
        }
