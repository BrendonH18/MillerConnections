from django import forms
from .models import Appointment, Customer

class AppointmentForm(forms.ModelForm):
    # Fields for the related Customer model
    customer_name = forms.CharField(max_length=255, required=True)
    customer_phone1 = forms.IntegerField(required=True)
    customer_phone2 = forms.IntegerField(required=False)
    customer_street = forms.CharField(max_length=255, required=True)
    customer_state = forms.CharField(max_length=255, required=True)
    # customer_complete = forms.CharField(max_length=255, required=True)
    customer_zip = forms.CharField(max_length=10, required=True)

    class Meta:
        model = Appointment
        fields = [
            'user_field_agent',
            'scheduled',
            # 'complete',
            # 'disposition',
            'recording',
        ]

    def save(self, commit=True, user=None):
        appointment = super().save(commit=False)
        if commit:
            customer = Customer.objects.create(
                name=self.cleaned_data['customer_name'],
                phone1=self.cleaned_data['customer_phone1'],
                phone2=self.cleaned_data['customer_phone2'],
                street=self.cleaned_data['customer_street'],
                state=self.cleaned_data['customer_state'],
                # complete=self.cleaned_data['customer_complete'],
                zip=self.cleaned_data['customer_zip'],
            )
            appointment.customer = customer
            if user:
                appointment.user_phone_agent = user
            appointment.save()
        return appointment
