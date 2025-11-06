from rest_framework import serializers
from authentication.models import User
from timesheet.models import TimeEntry


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee users"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'company_name',
            'role',
            'profile_image',
            'country',
            'is_email_verified',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry"""
    employee_name = serializers.CharField(source='user.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='user.email', read_only=True)
    employee_id = serializers.CharField(source='user.id', read_only=True)
    working_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeEntry
        fields = [
            'id',
            'employee_id',
            'employee_name',
            'employee_email',
            'date',
            'entry_time',
            'exit_time',
            'total_working_time',
            'working_hours',
            'attendance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
    
    def get_working_hours(self, obj):
        """Return formatted working hours"""
        return obj.get_working_hours()


class EmployeeTimesheetDetailSerializer(serializers.Serializer):
    """Serializer for detailed employee timesheet with all info"""
    employee = EmployeeSerializer(read_only=True)
    timesheet_entries = TimeEntrySerializer(many=True, read_only=True)
    total_hours_for_period = serializers.SerializerMethodField()
    total_entries = serializers.IntegerField(read_only=True)
    period_start = serializers.DateField(read_only=True)
    period_end = serializers.DateField(read_only=True)
    
    def get_total_hours_for_period(self, obj):
        """Calculate total hours for the period"""
        total_seconds = 0
        for entry in obj.get('timesheet_entries', []):
            if entry.total_working_time:
                total_seconds += int(entry.total_working_time.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
