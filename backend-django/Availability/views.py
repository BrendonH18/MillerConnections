# views.py

from django.http import JsonResponse
from django.views.generic import View
from .models import TimeSlot, Territory
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from dateutil import parser
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

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
        if not user_id:
            return JsonResponse({'error': 'User parameter missing'}, status=400)
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

                available_territories = Territory.objects.filter(
                    Q(user_id=user_id, is_active=True) | Q(user_id=user_id, is_default=True)
                    )
                # if not available_territories.exists():
                #     available_territories = Territory.objects.filter(user_id=user_id, is_default=True)
                if not available_territories.exists():
                    available_territories = [Territory.objects.create(
                        user=User.objects.filter(id=user_id).first(),
                        name="Default",
                        description="Placeholder",
                        is_active=False,
                        created_at=timezone.now(),
                        deleted_at=timezone.now(),
                        is_default=True
                    )]

                response_data = {
                    'possible_hours': possible_hours,
                    'week_start':start_of_week.strftime('%Y-%m-%d'),
                    'week_end': end_of_week.strftime('%Y-%m-%d'),
                    'available_times': [{'date': timeSlot.date.strftime('%Y-%m-%d'), 'time': timeSlot.hour, 'source': timeSlot.source, 'territory': getattr(timeSlot.territory, 'id', "")} for timeSlot in available_times],
                    'available_territories': [{'id': territory.id, 'name': territory.name} for territory in available_territories]
                }
                return JsonResponse(response_data, safe=False)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)
        else:
            return JsonResponse({'error': 'Date parameter missing'}, status=400)

@method_decorator(login_required, name='dispatch')
class ToggleTimeSlotByUser(View):
    def post(self, request, *args, **kwargs):
        required_fields = ['date', 'time', 'userId', 'territoryId']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)

        date = request.POST.get('date')
        time = request.POST.get('time')
        userId = request.POST.get('userId')
        territoryId = request.POST.get('territoryId')
        
        try:
            territory = Territory.objects.get(id=territoryId)
        except Territory.DoesNotExist:
            return JsonResponse({'error': 'territoryId not found'}, status=400)
        
        try:
            timeslots_to_update_territory = TimeSlot.objects.filter(user_id=userId, date=date)
            timeslots_to_update_territory.update(territory=territory)
        except:
            pass

        try:
            timeslot = TimeSlot.objects.get(user_id=userId, date=date, hour=time)
            if timeslot.source == 'system':
                timeslot.created_by = request.user
                timeslot.source = 'user'
                timeslot.territory = territory
                timeslot.save()
                action = 'updated'
            else:
                timeslot.delete()
                action = 'deleted'
        except TimeSlot.DoesNotExist:
            try:
                TimeSlot.objects.create(user_id=userId, date=date, hour=time, created_by=request.user, source='user', territory=territory)
                action = 'created'
            except Exception:
                return JsonResponse({'error': 'Failed to create TimeSlot'}, status=400)
        
        return JsonResponse({
            'action': action,
            'date': date,
            'time': time,
            'userId': userId,
            'territoryId': territoryId,
            'source': 'user'
        }, safe=False)
    
    # System Generated
    # User Generated, Previously Logged
    # User Updated, Current Session