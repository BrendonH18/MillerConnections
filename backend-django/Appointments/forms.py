from django import forms
from .models import Appointment, Customer, Disposition, Contract
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Q

User = get_user_model()

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        if hasattr(self, 'queryset'):
            value = self.queryset.get(pk=value).__str__()
        return format_html(f'<div class="readonly" >{value}</div>')

class AppointmentForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=255, required=True, label='Name')
    customer_phone1 = forms.IntegerField(required=True, label='Phone (Primary)')
    customer_phone2 = forms.IntegerField(required=False, label='Phone (Secondary)')
    customer_street = forms.CharField(max_length=255, required=True, label='Street')
    customer_state = forms.CharField(max_length=255, required=True, label='State')
    customer_zip = forms.CharField(max_length=10, required=True, label='Zip')
    recording = forms.CharField(widget=forms.TextInput(), required=False)
    scheduled = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    complete = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    user_field_agent = forms.ModelChoiceField(queryset=User.objects.filter(groups__name = "Field"), required=True, label='Field Agent')
    user_phone_agent = forms.ModelChoiceField(queryset=User.objects.filter(groups__name = "Phone"), required=True, label='Phone Agent')
    disposition = forms.ModelChoiceField(queryset=Disposition.objects.all(), required=True, label='Disposition')
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, label='Contract')

    class Meta:
        model = Appointment
        fields = [
            'user_field_agent',
            'user_phone_agent',
            'scheduled',
            'complete',
            'disposition',
            'recording',
            'contract'
            # 'customer',
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        customer = None
        appointment = None
        
        if self.instance:
            customer = getattr(self.instance, 'customer', None)
            # appointment = self.instance
            appointment = getattr(self, 'instance', None)

        # if appointment:
        #     if appointment.user_field_agent_id == True:
        #         self.fields['contract'].queryset = Contract.objects.filter(
        #             users=kwargs['instance'].user_field_agent,
        #             start_date__lte=timezone.now(),
        #             end_date__gte=timezone.now()
        #         )
        #     else:
        #         self.fields['contract'].queryset = Contract.objects.none()
        # else:
        #     self.fields['contract'].queryset = Contract.objects.none()

        lock_mapping = [
            (customer, 'customer_name', 'name'),
            (customer, 'customer_phone1', 'phone1'),
            (customer, 'customer_phone2', 'phone2'),
            (customer, 'customer_street', 'street'),
            (customer, 'customer_state', 'state'),
            (customer, 'customer_zip', 'zip'),
            (appointment, 'recording', 'recording'),
            (appointment, 'scheduled', 'scheduled'),
            (appointment, 'complete', 'complete'),
            (appointment, 'user_field_agent', 'user_field_agent'),
            (appointment, 'user_phone_agent', 'user_phone_agent'),
            (appointment, 'disposition', 'disposition'),
            (appointment, 'contract', 'contract')
        ]

        external_manager_lock_mapping = [
            (appointment, 'recording', 'recording'),
            (appointment, 'user_phone_agent', 'user_phone_agent'),
        ]

        phone_lock_mapping = [
            (appointment, 'user_phone_agent', 'user_phone_agent'),
        ]

        field_lock_mapping = [
            (customer, 'customer_name', 'name'),
            (customer, 'customer_phone1', 'phone1'),
            (customer, 'customer_phone2', 'phone2'),
            (customer, 'customer_street', 'street'),
            (customer, 'customer_state', 'state'),
            (customer, 'customer_zip', 'zip'),
            (appointment, 'recording', 'recording'),
            (appointment, 'user_field_agent', 'user_field_agent'),
            (appointment, 'user_phone_agent', 'user_phone_agent'),
        ]

        # If an instance is provided (i.e., editing an existing appointment),
        # populate the customer-related fields with the customer's data

        def is_in_X_lock_mapping(field_name, attr_name, lock_mapping):
            return any(field == field_name and attr == attr_name for _, field, attr in lock_mapping)
        
        def lock_field(field_name):
            attributes =['readonly', 'disabled']
            for attr in attributes:
                self.fields[field_name].widget.attrs[attr] = True

        if appointment and appointment.pk:
            # Set Initial Value
            # Make Every Value ReadOnly By Default
            for obj, field_name, attr_name in lock_mapping:
                self.fields[field_name].initial = getattr(obj, attr_name)
                if self.request:
                    if self.request.user.is_superuser:
                        continue
                    elif self.request.user.groups.filter(name="Internal Manager").exists():
                        continue
                    elif self.request.user.groups.filter(name="External Manager").exists():
                        if is_in_X_lock_mapping(field_name, attr_name, external_manager_lock_mapping):
                            lock_field(field_name)
                    elif self.request.user.groups.filter(name="Phone").exists():
                        if is_in_X_lock_mapping(field_name, attr_name, phone_lock_mapping):
                            lock_field(field_name)
                    elif self.request.user.groups.filter(name="Field").exists():
                        if is_in_X_lock_mapping(field_name, attr_name, field_lock_mapping):
                            lock_field(field_name)
                    else:
                        lock_field(field_name)    
                else:
                    lock_field(field_name)

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
                # if 'customer_name' in self.readonly_fields:
                #     customer.name = self.fields['customer_name'].initial
                # if 'customer_phone1' in self.readonly_fields:
                #     customer.phone1 = self.fields['customer_phone1'].initial
                # if 'customer_phone2' in self.readonly_fields:
                #     customer.phone2 = self.fields['customer_phone2'].initial
                # if 'customer_street' in self.readonly_fields:
                #     customer.street = self.fields['customer_street'].initial
                # if 'customer_state' in self.readonly_fields:
                #     customer.state = self.fields['customer_state'].initial
                # if 'customer_zip' in self.readonly_fields:
                #     customer.zip = self.fields['customer_zip'].initial

                customer.save()

            appointment.customer = customer
            # if user:
            #     appointment.user_phone_agent = user
            appointment.save()
        return appointment

# Not Being Used


    
class ReadOnlyAppointmentForm(AppointmentForm):
    def __init__(self, *args, **kwargs):
        normal_fields = ['customer_name']
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
                if field_name in normal_fields:
                    continue
                if hasattr(field, 'queryset'):
                    field.widget = ReadOnlyWidget()
                    field.widget.queryset = field.queryset
                else:
                    field.widget = ReadOnlyWidget()

    def save(self, commit=True, user=None):
        # Prevent saving as this form is read-only
        raise forms.ValidationError("This form is read-only and cannot be saved.")
