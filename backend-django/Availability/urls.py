# urls.py

from django.urls import path
from .views import TimeSlotListView,ToggleTimeSlot

urlpatterns = [
    # Other URL patterns
    path('retrieve_time_slots/', TimeSlotListView.as_view(), name='time_slot_list'),
    path('toggle_time_slot/', ToggleTimeSlot.as_view(), name='toggle_time_slot'),
]
