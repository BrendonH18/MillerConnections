# views.py

from django.http import JsonResponse
from django.views.generic import View
from .models import TimeSlot, Territory, Slot, Date
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from dateutil import parser
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.forms.models import model_to_dict
from .serializers import DateSerializer, SlotsSerializer, TerritorySerializer

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
        required_fields = ['date', 'time', 'userId', 'territoryId', 'source']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)

        date = request.POST.get('date')
        time = request.POST.get('time')
        userId = request.POST.get('userId')
        territoryId = request.POST.get('territoryId')
        source = request.POST.get('source')

        
        try:
            territory = Territory.objects.get(id=territoryId)
        except Territory.DoesNotExist:
            return JsonResponse({'error': 'territoryId not found'}, status=400)
        
        # Consider moving this to a different view. When the Territory at the top is changed, change all territories below.
        try:
            timeslot, isCreated = TimeSlot.objects.get_or_create(
                user_id=userId,
                date=date,
                hour=time,
                defaults={
                    'source': 'pending',
                    'created_by': request.user,
                    'territory': territory,
                })
            if timeslot:
                if source == 'button':
                    if timeslot.source == 'user':
                        timeslot.source = 'pending'
                    elif timeslot.source == 'pending':
                        timeslot.source = 'user'
                timeslot.created_by = request.user
                timeslot.territory = territory
                timeslot.save()
                action = 'updated'
            else:
                return JsonResponse({'error': 'Failed to create TimeSlot'}, status=400)
        except:
            pass

        timeslot_dict = model_to_dict(timeslot)
        timeslot_dict['action'] = action
        return JsonResponse(timeslot_dict, safe=False)
    
    # System Generated
    # User Generated, Previously Logged
    # User Updated, Current Session

import calendar
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render

def parse_date(date_str):
    # Strip any leading or trailing whitespace
    date_str = date_str.strip()

    # Check if the string contains time information
    if 'AM' in date_str or 'PM' in date_str:
        # Parse the string with date and time
        return datetime.strptime(date_str, '%m/%d/%Y %I:%M %p')
    else:
        # Parse the string with only the date
        return datetime.strptime(date_str, '%m/%d/%Y')
    
# @method_decorator(login_required, name='dispatch')
class generate_calendar(View):
    def get(self, request, *args, **kwargs):
        required_fields = ['user_id', 'date']
        missing_fields = [field for field in required_fields if not request.GET.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)
        # Get the timestamp from the request (e.g., Date.now() = 1720043153382)
        user_id = request.GET.get('user_id')
        date_str = request.GET.get('date')
        # timestamp = int(request.GET.get('timestamp', 0)) / 1000
        current_date = parse_date(date_str)
        # current_date = datetime(date_str)

        # Determine the month and year
        year = current_date.year
        month = current_date.month

        # Create a calendar for the specified month and year
        cal = calendar.Calendar(firstweekday=6)  # Start with Sunday
        month_days = cal.monthdayscalendar(year, month)


        month_days_w_mixins = []
        try:

            for week_num in list(range(0, len(month_days))):
                week = []
                for day_num in list(range(0, len(month_days[week_num]))):
                    day = {}
                    if month_days[week_num][day_num] == 0:
                        day['date'] = 0
                        day['date_obj'] = None
                        week.append(day)
                        continue
                    date = datetime(year=year, month=month, day=month_days[week_num][day_num])
                    _date, _date_is_new = Date.objects.get_or_create(date=date, user_id=int(user_id))
                    day['date'] = date
                    day['date_obj'] = DateSerializer(_date).data
                    # day['slots'] = _date.slots.all()
                    week.append(day)
                    
                month_days_w_mixins.append(week)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

                                                


        # Format the calendar data
        days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        calendar_data = {
            'days_of_week': days_of_week,
            'weeks': month_days_w_mixins
        }

        return JsonResponse(calendar_data)
    

class generate_slots(View):
    def get(self, request, *args, **kwargs):
        required_fields = ['date_id']
        missing_fields = [field for field in required_fields if not request.GET.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)
        # Get the timestamp from the request (e.g., Date.now() = 1720043153382)
        date_id = request.GET.get('date_id')

        date_obj = Date.objects.get(id=int(date_id))

        slots = date_obj.slots.all().order_by('start_time')
        serialized_slots = SlotsSerializer(slots, many=True).data
        data = {
            "slots": serialized_slots
        }
        return JsonResponse(data)
    
class update_slot(View):
    def post(self, request, *args, **kwargs):
        required_fields = ['slot_id']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)
        # Get the timestamp from the request (e.g., Date.now() = 1720043153382)
        slot_id = request.POST.get('slot_id')

        try:
            # Fetch the slot object
            slot_obj = Slot.objects.get(id=int(slot_id))

            # Toggle the status
            if slot_obj.status == 'unavailable':
                slot_obj.status = 'available'
            else:
                slot_obj.status = 'unavailable'

            # Update the user who made the change
            slot_obj.update_availability_user = request.user

            # Save the changes to the database
            slot_obj.save()

            return JsonResponse({'message': 'Slot updated successfully', 'status': slot_obj.status}, status=200)

        except Slot.DoesNotExist:
            return JsonResponse({'error': 'Slot not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class Territories(View):
    def get(self, request, *args, **kwargs):
        required_fields = ['slot_id']
        missing_fields = [field for field in required_fields if not request.GET.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)
        # Get the timestamp from the request (e.g., Date.now() = 1720043153382)
        slot_id = request.GET.get('slot_id')

        try:
            # Fetch the slot object
            slot_obj = Slot.objects.get(id=int(slot_id))

            user = slot_obj.date.user
            active_territories = TerritorySerializer(Territory.objects.filter(user=user, is_active=True)).data

            return JsonResponse({'message': 'Slot updated successfully', 'territories': active_territories}, status=200)

        except Slot.DoesNotExist:
            return JsonResponse({'error': 'Territory not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request, *args, **kwargs):
        required_fields = ['slot_id', 'territory_id']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            return JsonResponse({'error': f'{", ".join(missing_fields)} parameter(s) missing'}, status=400)
        # Get the timestamp from the request (e.g., Date.now() = 1720043153382)
        slot_id = request.POST.get('slot_id')
        territory_id = request.POST.get('territory_id')

        try:
            # Fetch the slot object
            slot_obj = Slot.objects.get(id=int(slot_id))
            territory_obj = Territory.objects.get(id=int(territory_id))

            slot_obj.territory = territory_obj
            slot_obj.save()

            return JsonResponse({'message': 'Slot updated successfully', 'territory': territory_id}, status=200)

        except Slot.DoesNotExist:
            return JsonResponse({'error': 'Territory not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)