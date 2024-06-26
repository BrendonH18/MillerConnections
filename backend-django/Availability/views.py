# views.py

from django.http import JsonResponse
from django.views.generic import View
from .models import TimeSlot
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from dateutil import parser

def parse_date(date_str):
    try:
        # Use dateutil.parser to parse the date string
        dt = parser.parse(date_str)
        # Return only the date part
        return dt.date()
    except ValueError:
        # Handle the case where the date string cannot be parsed
        print("Error: Unable to parse the date string")
        return None
    
@method_decorator(login_required, name='dispatch')
class TimeSlotListView(View):
    
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)
        try:
            date = parse_date(date_str)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Date should be in YYYY-MM-DD format.'}, status=400)

        if date:
            try:
                possible_hours = [hour[0] for hour in TimeSlot.HOUR_CHOICES]
                # Determine the start and end of the week
                start_of_week = date - timedelta(days=date.weekday() + 1)
                end_of_week = start_of_week + timedelta(days=6)

                available_times = TimeSlot.objects.filter(
                    user_id=user_id,
                    date__range=[start_of_week, end_of_week]
                )
                response_data = {
                    'possible_hours': possible_hours,
                    'week_start':start_of_week.strftime('%Y-%m-%d'),
                    'week_end': end_of_week.strftime('%Y-%m-%d'),
                    'available_times': [{'date': timeSlot.date.strftime('%Y-%m-%d'), 'time': timeSlot.hour, 'source': timeSlot.source} for timeSlot in available_times]
                }
                return JsonResponse(response_data, safe=False)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)
        else:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)

@method_decorator(login_required, name='dispatch')
class ToggleTimeSlot_by_User(View):
    def post(self, request, *args, **kwargs):
        date = request.POST.get('date')
        time = request.POST.get('time')
        userId = request.POST.get('userId')
        if not date:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)
        if not time:
            return JsonResponse({'error': 'Time parameter missing'}, status=400)
        if not userId:
            return JsonResponse({'error': 'userId parameter missing'}, status=400)
        
        action = "none"
        
        try:
            timeslot = TimeSlot.objects.get(user_id=userId, date=date, hour=time)
            if timeslot.source == 'system':
                timeslot.created_by = request.user
                timeslot.source = 'user'
                timeslot.save()
                action = 'updated'
            else:
                timeslot.delete()
                action = 'deleted'
        except TimeSlot.DoesNotExist:
            # TimeSlot does not exist, create it
            TimeSlot.objects.create(user_id=userId, date=date, hour=time, created_by=request.user, source='user')
            action = 'created'
        response_data = {
            'action': action,
            'date': date,
            'time': time,
            'userId':userId
        }
        return JsonResponse(response_data, safe=False)