from django.shortcuts import render
from rest_framework import generics
from .models import Appointment, Contract
from .serializers import AppointmentSerializer
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Case, When, BooleanField, Value
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

User = get_user_model()

@method_decorator(login_required, name='dispatch')
class AppointmentList(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@login_required
def get_contracts(request):
    user_field_agent_id = request.POST.get('user_field_agent_id')
    contracts = {}
    try:
        if user_field_agent_id:
            user = User.objects.get(pk = user_field_agent_id)
            contracts = Contract.objects.filter(users=user).annotate(
                is_active=Case(
                    When(start_date__lte=timezone.now(), end_date__gte=timezone.now(), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )).filter(is_active=True)
            contracts_list = [{'value': contract.id, 'text': contract.name} for contract in contracts]
    except:
        pass
    return JsonResponse(data={'contracts': contracts_list}, safe=False)