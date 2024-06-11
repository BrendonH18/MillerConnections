from django.shortcuts import render
from rest_framework import generics
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentList(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

