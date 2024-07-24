# serializers.py
from rest_framework import serializers
from .models import Date, Slot, Territory
from datetime import datetime

class CustomDateField(serializers.Field):
    def to_representation(self, value):
        # Ensure the value is a date object
        if isinstance(value, datetime):
            return value.date().isoformat()
        return value.isoformat()

    def to_internal_value(self, data):
        # Parse the input date string
        try:
            return datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError('Invalid date format. Expected YYYY-MM-DD')

class SlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'

class DateSerializer(serializers.ModelSerializer):
    # slots = SlotsSerializer(many=True, read_only=True)
    date = CustomDateField()

    class Meta:
        model = Date
        fields = ["date", "status", "territory", "user", "id"]

class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = ["id", "name", "description", "is_default"]
