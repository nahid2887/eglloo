from rest_framework import serializers
from authentication.models import User
from timesheet.models import TimeEntry
from .models import Project, Task, ProjectDocument


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


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task - assigned_employee_id accepts User ID and validates Employee role"""
    assigned_employee_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True,
        help_text="User ID of the Employee to assign this task to"
    )
    assigned_employee_name = serializers.SerializerMethodField()
    assigned_employee = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
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
            'assigned_employee_id',
            'assigned_employee',
            'assigned_employee_name',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'project', 'created_by', 'assigned_employee', 'assigned_employee_name', 'created_at', 'updated_at']
        extra_kwargs = {
            'task_name': {'required': True},
            'priority': {'required': True},
            'due_date': {'required': True},
        }
    
    def validate(self, data):
        """Custom validation to catch common mistakes"""
        # Get the initial data from the request
        if hasattr(self, 'initial_data'):
            # Check if user mistakenly used 'assigned_employee' instead of 'assigned_employee_id'
            if 'assigned_employee' in self.initial_data and 'assigned_employee_id' not in self.initial_data:
                raise serializers.ValidationError({
                    'assigned_employee': 'Invalid field. Use "assigned_employee_id" (integer) to assign an employee, not "assigned_employee".'
                })
        return data
    
    def validate_assigned_employee_id(self, value):
        """Validate and resolve ID to an Employee user from the same company"""
        if value is None:
            return None  # Allow None (unassigned tasks)
        
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"User with ID {value} not found."
            )
        
        # Check if user has Employee role
        if not hasattr(user, 'role') or user.role != 'Employee':
            current_role = getattr(user, 'role', 'Unknown')
            raise serializers.ValidationError(
                f"Cannot assign task to user ID {value}. User must have 'Employee' role. Current role: '{current_role}'"
            )
        
        # Check if employee belongs to the same company as the project manager
        request_user = self.context.get('request').user if self.context.get('request') else None
        if request_user and hasattr(request_user, 'company_name') and hasattr(user, 'company_name'):
            if request_user.company_name != user.company_name:
                raise serializers.ValidationError(
                    f"Cannot assign task to employee '{user.username}'. Employee must belong to the same company. "
                    f"Your company: '{request_user.company_name}', Employee's company: '{user.company_name}'"
                )
        
        return user
    
    def create(self, validated_data):
        """Create task and assign to the resolved employee"""
        assigned_employee_id = validated_data.pop('assigned_employee_id', None)
        
        task = Task.objects.create(**validated_data)
        
        if assigned_employee_id:
            task.assigned_employee = assigned_employee_id
            task.save()
        
        return task
    
    def update(self, instance, validated_data):
        """Update task and assign to the resolved employee"""
        assigned_employee_id = validated_data.pop('assigned_employee_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if assigned_employee_id is not None:
            instance.assigned_employee = assigned_employee_id
        
        instance.save()
        return instance
    
    def get_assigned_employee_name(self, obj):
        """Get assigned employee full name and username"""
        if obj.assigned_employee:
            full_name = f"{obj.assigned_employee.first_name} {obj.assigned_employee.last_name}".strip() or obj.assigned_employee.username
            return full_name
        return None
    
    def get_assigned_employee(self, obj):
        """Get assigned employee full details"""
        if obj.assigned_employee:
            # Safely get profile_image URL
            profile_image_url = None
            if hasattr(obj.assigned_employee, 'profile_image') and obj.assigned_employee.profile_image:
                try:
                    profile_image_url = obj.assigned_employee.profile_image.url
                except (ValueError, AttributeError):
                    profile_image_url = None
            
            return {
                'id': obj.assigned_employee.id,
                'username': obj.assigned_employee.username,
                'email': obj.assigned_employee.email,
                'first_name': obj.assigned_employee.first_name,
                'last_name': obj.assigned_employee.last_name,
                'full_name': f"{obj.assigned_employee.first_name} {obj.assigned_employee.last_name}".strip() or obj.assigned_employee.username,
                'role': getattr(obj.assigned_employee, 'role', 'Unknown'),
                'company_name': getattr(obj.assigned_employee, 'company_name', None),
                'profile_image': profile_image_url,
            }
        return None
    
    def get_created_by_name(self, obj):
        """Get creator full name"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for Project list view"""
    tasks_count = serializers.SerializerMethodField()
    assigned_employees_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    
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
            'rooms',
            'tasks_count',
            'assigned_employees_count',
            'created_by_name',
            'assigned_to_name',
            'created_at',
        ]
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()
    
    def get_assigned_employees_count(self, obj):
        """Get count of unique employees assigned to tasks"""
        return obj.tasks.filter(assigned_employee__isnull=False).values('assigned_employee').distinct().count()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for Project detail view with tasks and documents"""
    tasks = TaskSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True)
    tasks_count = serializers.SerializerMethodField()
    assigned_employees_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    estimate_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id',
            'estimate',
            'estimate_info',
            'project_name',
            'client_name',
            'description',
            'status',
            'creating_date',
            'start_date',
            'end_date',
            'total_amount',
            'estimated_cost',
            'rooms',
            'tasks',
            'tasks_count',
            'documents',
            'assigned_employees_count',
            'created_by',
            'created_by_name',
            'assigned_to',
            'assigned_to_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'estimate', 'created_at', 'updated_at', 'created_by']
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()
    
    def get_assigned_employees_count(self, obj):
        """Get count of unique employees assigned to tasks"""
        return obj.tasks.filter(assigned_employee__isnull=False).values('assigned_employee').distinct().count()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None
    
    def get_estimate_info(self, obj):
        """Return basic estimate info"""
        if obj.estimate:
            return {
                'id': obj.estimate.id,
                'serial_number': obj.estimate.serial_number,
                'estimate_number': obj.estimate.estimate_number,
                'status': obj.estimate.status,
                'total_cost': float(obj.estimate.total_cost),
            }
        return None


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a project from an estimate"""
    
    class Meta:
        model = Project
        fields = [
            'estimate',
            'project_name',
            'client_name',
            'description',
            'start_date',
            'end_date',
            'assigned_to',
        ]
    
    def create(self, validated_data):
        """Create project from estimate"""
        estimate = validated_data.get('estimate')
        
        # Populate project data from estimate
        validated_data['total_amount'] = estimate.total_with_tax
        validated_data['estimated_cost'] = estimate.total_cost
        validated_data['rooms'] = estimate.targeted_rooms or []
        
        project = Project.objects.create(**validated_data)
        return project


class TaskGanttSerializer(serializers.ModelSerializer):
    """Serializer for Gantt/Grid chart view - shows task timeline"""
    assigned_employee_name = serializers.SerializerMethodField()
    room = serializers.CharField(allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'task_name',
            'room',
            'start_date',
            'due_date',
            'status',
            'priority',
            'phase',
            'assigned_employee',
            'assigned_employee_name',
        ]
    
    def get_assigned_employee_name(self, obj):
        """Get assigned employee username"""
        if obj.assigned_employee:
            return obj.assigned_employee.username
        return None


class ProjectGanttSerializer(serializers.Serializer):
    """Serializer for Project Gantt/Grid chart view"""
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    client_name = serializers.CharField()
    status = serializers.CharField()
    project_start_date = serializers.DateField()
    project_end_date = serializers.DateField(allow_null=True)
    total_tasks = serializers.IntegerField()
    tasks = TaskGanttSerializer(many=True, read_only=True)
    
    class Meta:
        fields = [
            'project_id',
            'project_name',
            'client_name',
            'status',
            'project_start_date',
            'project_end_date',
            'total_tasks',
            'tasks',
        ]


class ProjectManagerAssignedProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project Manager to view all projects with progress"""
    progress = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
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
        
        today = timezone.now().date()
        days_left = (obj.end_date - today).days
        
        if days_left < 0:
            return f"{abs(days_left)} days left to deliver"
        elif days_left == 0:
            return "Due today"
        else:
            return f"{days_left} days left to deliver"

class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDocument"""
    uploaded_by_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectDocument
        fields = [
            'id',
            'project',
            'document_name',
            'document_type',
            'file',
            'file_url',
            'file_size',
            'description',
            'uploaded_by',
            'uploaded_by_name',
            'uploaded_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'project', 'uploaded_by', 'created_at', 'updated_at']
    
    def get_uploaded_by_name(self, obj):
        """Get uploader full name"""
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip() or obj.uploaded_by.username
        return None
    
    def get_file_url(self, obj):
        """Get file URL"""
        if obj.file:
            try:
                return obj.file.url
            except (ValueError, AttributeError):
                return None
        return None
    
    def get_file_size(self, obj):
        """Get file size in bytes"""
        if obj.file:
            try:
                return obj.file.size
            except (ValueError, AttributeError):
                return None
        return None