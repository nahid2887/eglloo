from rest_framework import serializers
from authentication.models import User
from Project_manager.models import Task, Project


class EmployeeProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project information in task context"""
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id',
            'project_name',
            'client_name',
            'status',
            'creating_date',
            'start_date',
            'end_date',
            'total_amount',
            'estimated_cost',
            'rooms',
            'created_by_name',
        ]
    
    def get_created_by_name(self, obj):
        """Get creator full name"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class EmployeeAssignedTaskSerializer(serializers.ModelSerializer):
    """Serializer for Task - for employee viewing their assigned tasks"""
    project_details = EmployeeProjectSerializer(source='project', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'project_details',
            'task_name',
            'description',
            'room',
            'status',
            'priority',
            'phase',
            'start_date',
            'due_date',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'project',
            'task_name',
            'description',
            'room',
            'status',
            'priority',
            'phase',
            'start_date',
            'due_date',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
    
    def get_created_by_name(self, obj):
        """Get creator full name"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class EmployeeTaskStatsSerializer(serializers.Serializer):
    """Serializer for employee task statistics"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    due_tasks = serializers.IntegerField()
    upcoming_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    not_started_tasks = serializers.IntegerField()


class EmployeeAssignedProjectSerializer(serializers.ModelSerializer):
    """Serializer for Employee to view their assigned projects with progress"""
    progress = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    assigned_tasks_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    deadline_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id',
            'project_name',
            'client_name',
            'description',
            'status',
            'progress',
            'creating_date',
            'start_date',
            'end_date',
            'deadline_status',
            'total_amount',
            'estimated_cost',
            'rooms',
            'total_tasks',
            'assigned_tasks_count',
            'completed_tasks',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
    
    def get_progress(self, obj):
        """Calculate progress percentage based on completed tasks"""
        total_tasks = obj.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = obj.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)
    
    def get_total_tasks(self, obj):
        """Get total number of tasks in the project"""
        return obj.tasks.count()
    
    def get_completed_tasks(self, obj):
        """Get number of completed tasks"""
        return obj.tasks.filter(status='completed').count()
    
    def get_assigned_tasks_count(self, obj):
        """Get number of tasks assigned to this employee"""
        employee = self.context.get('employee')
        if employee:
            return obj.tasks.filter(assigned_employee=employee).count()
        return 0
    
    def get_created_by_name(self, obj):
        """Get project creator's full name"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None
    
    def get_deadline_status(self, obj):
        """Check if project is overdue or how many days left"""
        if not obj.end_date:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        days_left = (obj.end_date - today).days
        
        if days_left < 0:
            return f"{abs(days_left)} days left to deliver"
        elif days_left == 0:
            return "Due today"
        else:
            return f"{days_left} days left to deliver"


class TaskTimerSerializer(serializers.ModelSerializer):
    """Serializer for TaskTimer"""
    task_id = serializers.IntegerField(source='task.id', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    task_status = serializers.CharField(source='task.status', read_only=True)
    project_id = serializers.IntegerField(source='task.project.id', read_only=True)
    project_name = serializers.CharField(source='task.project.project_name', read_only=True)
    #project_status = serializers.CharField(source='task.project.status', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        from .models import TaskTimer
        model = TaskTimer
        fields = [
            'id',
            'employee',
            'employee_name',
            'task',
            'task_id',
            'task_name',
            'task_status',
            'project_id',
            'project_name',
            #'project_status',
            'work_date',
            'start_time',
            'end_time',
            'duration_seconds',
            'duration_formatted',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'work_date', 'duration_seconds', 'created_at', 'updated_at']
    
    def get_duration_formatted(self, obj):
        """Get formatted duration"""
        return obj.get_duration_formatted()
    
    def get_employee_name(self, obj):
        """Get employee full name"""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}".strip() or obj.employee.username
        return None
