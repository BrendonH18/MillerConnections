from rest_framework import serializers
from .models import Appointment, Note, Disposition
from Customers.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email', 'first_name', 'last_name']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['pk', 'name', 'phone1', 'phone2', 'street', 'state', 'zip', 'complete']

class DispositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disposition
        fields = ['pk', 'name']

class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Note
        fields = ['pk', 'user', 'text', 'created_at']

class AppointmentSerializer(serializers.ModelSerializer):
    user_phone_agent = UserSerializer()
    user_field_agent = UserSerializer()
    customer = CustomerSerializer()
    disposition = DispositionSerializer()
    notes = NoteSerializer(many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        all_dispositions = Disposition.objects.all()
        representation['disposition']['options'] = DispositionSerializer(all_dispositions, many=True).data
        return representation

    class Meta:
        model = Appointment
        fields = ['appointment_id', 'created_at', 'user_phone_agent', 'user_field_agent', 'customer', 'scheduled', 'complete', 'disposition', 'recording', 'notes']
