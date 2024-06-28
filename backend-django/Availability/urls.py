# urls.py

from django.urls import path
from .views import TimeSlotListView,ToggleTimeSlotByUser

urlpatterns = [
    # Other URL patterns
    path('retrieve_time_slots/', TimeSlotListView.as_view(), name='time_slot_list'),
    path('toggle_time_slot_by_user/', ToggleTimeSlotByUser.as_view(), name='toggle_time_slot'),
]
