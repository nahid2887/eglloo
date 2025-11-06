from rest_framework import serializers
from .models import TimeEntry
from django.utils import timezone


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for time entry with calculated fields"""
    working_hours = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_email', 'user_name', 'date',
            'entry_time', 'exit_time', 'total_working_time',
            'working_hours', 'attendance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_working_time', 'attendance', 'created_at', 'updated_at']
        ref_name = 'TimesheetTimeEntry'
    
    def get_working_hours(self, obj):
        return obj.get_working_hours()
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class StartTimeSerializer(serializers.Serializer):
    """Serializer for starting time entry"""
    entry_time = serializers.TimeField(required=False)
    date = serializers.DateField(required=False)
    
    class Meta:
        ref_name = 'TimesheetStartTime'
    
    def validate(self, attrs):
        # Default to current time if not provided
        if 'entry_time' not in attrs:
            attrs['entry_time'] = timezone.now().time()
        
        # Default to today if not provided
        if 'date' not in attrs:
            attrs['date'] = timezone.now().date()
        
        return attrs


class EndTimeSerializer(serializers.Serializer):
    """Serializer for ending time entry"""
    exit_time = serializers.TimeField(required=False)
    
    class Meta:
        ref_name = 'TimesheetEndTime'
    
    def validate(self, attrs):
        # Default to current time if not provided
        if 'exit_time' not in attrs:
            attrs['exit_time'] = timezone.now().time()
        
        return attrs


class WeeklyHoursSerializer(serializers.Serializer):
    """Serializer for weekly hours summary"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    total_hours = serializers.IntegerField(read_only=True)
    total_minutes = serializers.IntegerField(read_only=True)
    formatted = serializers.CharField(read_only=True)
    entries = TimeEntrySerializer(many=True, read_only=True)
    
    class Meta:
        ref_name = 'TimesheetWeeklyHours'


class AttendanceSummarySerializer(serializers.Serializer):
    """Serializer for attendance summary"""
    date = serializers.DateField()
    in_time = serializers.TimeField(source='entry_time')
    out_time = serializers.TimeField(source='exit_time')
    total_working_time = serializers.CharField(source='get_working_hours')
    attendance = serializers.CharField()
    
    class Meta:
        ref_name = 'TimesheetAttendanceSummary'
