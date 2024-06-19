# views.py

from django.http import JsonResponse
from django.views.generic import View
from .models import TimeSlot
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta

class TimeSlotListView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Date should be in YYYY-MM-DD format.'}, status=400)

        if date_str:
            try:
                possible_hours = [hour[0] for hour in TimeSlot.HOUR_CHOICES]

                # Convert date string to datetime object
                date = datetime.strptime(date_str, '%Y-%m-%d').date()

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
                    'available_times': [{'date': time.date.strftime('%Y-%m-%d'), 'time': time.hour} for time in available_times]
                }
                return JsonResponse(response_data, safe=False)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)
        else:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)

class ToggleTimeSlot(View):
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
        
        try:
            timeslot = TimeSlot.objects.get(user_id=userId, date=date, hour=time)
            # TimeSlot exists, delete it
            timeslot.delete()
            action = 'deleted'
        except TimeSlot.DoesNotExist:
            # TimeSlot does not exist, create it
            TimeSlot.objects.create(user_id=userId, date=date, hour=time)
            action = 'created'
        response_data = {
            'action': action,
            'date': date,
            'time': time,
            'userId':userId
        }
        return JsonResponse(response_data, safe=False)