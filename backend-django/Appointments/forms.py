from django import forms
from .models import Appointment, Customer, Disposition
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe

User = get_user_model()
    
class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer)
        script = '''
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                var datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
                datetimeInputs.forEach(function(input) {
                    input.addEventListener('change', function() {
                        var value = input.value;
                        if (value) {
                            var date = new Date(value);
                            var minutes = date.getMinutes();
                            var newMinutes = minutes >= 30 ? 30 : 0;
                            date.setMinutes(newMinutes, 0, 0);
                            var newValue = date.toISOString().slice(0, 16);
                            input.value = newValue;
                        }
                    });
                });
            });
            </script>
        '''
        return mark_safe(rendered + script)

class AppointmentForm(forms.ModelForm):
    # Fields for the related Customer model
    customer_name = forms.CharField(max_length=255, required=True, label='Name')
    customer_phone1 = forms.IntegerField(required=True, label='Phone (Primary)')
    customer_phone2 = forms.IntegerField(required=False, label='Phone (Secondary)')
    customer_street = forms.CharField(max_length=255, required=True, label='Street')
    customer_state = forms.CharField(max_length=255, required=True, label='State')
    customer_zip = forms.CharField(max_length=10, required=True, label='Zip')
    recording = forms.CharField(widget=forms.TextInput(), required=False)
    scheduled = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    complete = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    user_field_agent = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label='Field Agent')
    user_phone_agent = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label='Phone Agent')
    disposition = forms.ModelChoiceField(queryset=Disposition.objects.all(), required=True, label='Disposition')


    class Meta:
        model = Appointment
        fields = [
            'user_field_agent',
            'user_phone_agent',
            'scheduled',
            'complete',
            'disposition',
            'recording',
        ]

    def __init__(self, *args, **kwargs):
        # Call the base class method to initialize the form
        super().__init__(*args, **kwargs)

        # If an instance is provided (i.e., editing an existing appointment),
        # populate the customer-related fields with the customer's data
        if self.instance and self.instance.pk:
            customer = self.instance.customer
            self.fields['customer_name'].initial = customer.name
            self.fields['customer_phone1'].initial = customer.phone1
            self.fields['customer_phone2'].initial = customer.phone2
            self.fields['customer_street'].initial = customer.street
            self.fields['customer_state'].initial = customer.state
            self.fields['customer_zip'].initial = customer.zip

    def save(self, commit=True, user=None):
        appointment = super().save(commit=False)
        if commit:
            if not appointment.customer_id:
                customer = Customer.objects.create(
                    name=self.cleaned_data['customer_name'],
                    phone1=self.cleaned_data['customer_phone1'],
                    phone2=self.cleaned_data['customer_phone2'],
                    street=self.cleaned_data['customer_street'],
                    state=self.cleaned_data['customer_state'],
                    zip=self.cleaned_data['customer_zip'],
                )
                appointment.customer = customer
            else:
                customer = appointment.customer
                customer.name = self.cleaned_data['customer_name']
                customer.phone1 = self.cleaned_data['customer_phone1']
                customer.phone2 = self.cleaned_data['customer_phone2']
                customer.street = self.cleaned_data['customer_street']
                customer.state = self.cleaned_data['customer_state']
                customer.zip = self.cleaned_data['customer_zip']
                customer.save()

            appointment.customer = customer
            if user:
                appointment.user_phone_agent = user
            appointment.save()
        return appointment

# Not Being Used

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        if hasattr(self, 'queryset'):
            value = self.queryset.get(pk=value).__str__()
        return format_html(f'<div class="readonly">{value}</div>')
    
class ReadOnlyAppointmentForm(AppointmentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
                if hasattr(field, 'queryset'):
                    field.widget = ReadOnlyWidget()
                    field.widget.queryset = field.queryset
                else:
                    field.widget = ReadOnlyWidget()

    def save(self, commit=True, user=None):
        # Prevent saving as this form is read-only
        raise forms.ValidationError("This form is read-only and cannot be saved.")
