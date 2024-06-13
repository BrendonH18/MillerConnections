from django.urls import path
from .views import AppointmentList, get_contracts

urlpatterns = [
    path('all/', AppointmentList.as_view(), name='appointment-list'),
    path('get_contracts/', get_contracts, name="get_contracts")
]