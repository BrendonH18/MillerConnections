from django import forms
from .models import Appointment, Customer

class AppointmentForm(forms.ModelForm):
    # Fields for the related Customer model
    customer_name = forms.CharField(max_length=255, required=True, label='Name')
    customer_phone1 = forms.IntegerField(required=True, label='Phone (Primary)')
    customer_phone2 = forms.IntegerField(required=False, label='Phone (Secondary)')
    customer_street = forms.CharField(max_length=255, required=True, label='Street')
    customer_state = forms.CharField(max_length=255, required=True, label='State')
    customer_zip = forms.CharField(max_length=10, required=True, label='Zip')
    recording = forms.CharField(widget=forms.TextInput(), required=False)
    # scheduled = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    # complete = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))


    class Meta:
        model = Appointment
        fields = [
            'user_field_agent',
            'scheduled',
            # 'complete',
            # 'disposition',
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
    

class ReadOnlyAppointmentForm(AppointmentForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            field.widget.attrs['disabled'] = True

    def save(self, commit=True, user=None):
        # Prevent saving as this form is read-only
        raise forms.ValidationError("This form is read-only and cannot be saved.")
