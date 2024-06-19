# urls.py

from django.urls import path
from .views import TimeSlotListView,ToggleTimeSlot_by_User

urlpatterns = [
    # Other URL patterns
    path('retrieve_time_slots/', TimeSlotListView.as_view(), name='time_slot_list'),
    path('toggle_time_slot_by_user/', ToggleTimeSlot_by_User.as_view(), name='toggle_time_slot'),
]
