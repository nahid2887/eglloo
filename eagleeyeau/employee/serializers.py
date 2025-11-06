from rest_framework import serializers
from .models import TimeEntry
from django.utils import timezone


class EmployeeTimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for employee time entry with calculated fields"""
    working_hours_display = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_email', 'user_name', 'date',
            'entry_time', 'exit_time', 'total_working_time',
            'working_hours_display', 'attendance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_working_time', 'attendance', 'created_at', 'updated_at']
        ref_name = 'EmployeeTimeEntry'
    
    def get_working_hours_display(self, obj):
        return obj.get_working_hours()
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.email


class StartTimeSerializer(serializers.Serializer):
    """Serializer for starting time entry - defaults to current time"""
    class Meta:
        ref_name = 'EmployeeStartTime'


class EndTimeSerializer(serializers.Serializer):
    """Serializer for ending time entry - defaults to current time"""
    class Meta:
        ref_name = 'EmployeeEndTime'


class WeeklyHoursSerializer(serializers.Serializer):
    """Serializer for weekly hours summary"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    total_hours = serializers.IntegerField(read_only=True)
    total_minutes = serializers.IntegerField(read_only=True)
    formatted = serializers.CharField(read_only=True)
    entries = EmployeeTimeEntrySerializer(many=True, read_only=True)
    
    class Meta:
        ref_name = 'EmployeeWeeklyHours'
