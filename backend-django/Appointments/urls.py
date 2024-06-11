from django.urls import path
from .views import AppointmentList

urlpatterns = [
    path('appointments/', AppointmentList.as_view(), name='appointment-list'),
]