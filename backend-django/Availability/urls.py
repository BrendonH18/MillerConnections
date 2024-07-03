# urls.py

from django.urls import path
from .views import TimeSlotListView,ToggleTimeSlotByUser,generate_calendar

urlpatterns = [
    # Other URL patterns
    path('retrieve_time_slots/', TimeSlotListView.as_view(), name='time_slot_list'),
    path('toggle_time_slot_by_user/', ToggleTimeSlotByUser.as_view(), name='toggle_time_slot'),
    path('generate_calendar/', generate_calendar.as_view(), name='generate_calendar'),
]
