from django.db import models
from django.conf import settings
from estimator.models import Estimate


class Project(models.Model):
    """
    Project model created from an approved Estimate.
    Project Manager can manage projects and add tasks.
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Link to the Estimate
    estimate = models.OneToOneField(Estimate, on_delete=models.PROTECT, related_name='project')
    
    # Project Info
    project_name = models.CharField(max_length=300)
    client_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    # Project Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Dates
    creating_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Financial Info (from Estimate)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Rooms (from Estimate targeted_rooms)
    rooms = models.JSONField(default=list, blank=True, help_text="Array of rooms for the project")
    
    # Management
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creating_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-creating_date']),
        ]
    
    def __str__(self):
        return f"{self.project_name} - {self.client_name}"


class ProjectDocument(models.Model):
    """
    Model to store documents/files associated with a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=300, help_text="Name or title of the document")
    document_type = models.CharField(
        max_length=50,
        default='pdf',
        help_text="File type (pdf, image, doc, etc.)"
    )
    file = models.FileField(
        upload_to='project_documents/%Y/%m/%d/',
        help_text="The actual file"
    )
    description = models.TextField(null=True, blank=True, help_text="Optional description of the document")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_project_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.document_name} - {self.project.project_name}"


class Task(models.Model):
    """
    Task model for individual tasks within a project.
    """
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]
    
    PHASE_CHOICES = [
        ('planning', 'Planning'),
        ('design', 'Design'),
        ('procurement', 'Procurement'),
        ('construction', 'Construction'),
        ('handover', 'Handover'),
    ]
    
    # Link to Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    
    # Task Info
    task_name = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    room = models.CharField(max_length=200, null=True, blank=True, help_text="Targeted room for this task")
    
    # Task Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, null=True, blank=True, help_text="Project phase for this task")
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Assignment
    assigned_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    
    class Meta:
        ordering = ['priority', 'due_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_employee']),
        ]
    
    def __str__(self):
        return f"{self.task_name} - {self.project.project_name}"


# ====================== SIGNALS FOR AUTOMATIC PROJECT STATUS UPDATE ======================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=Task)
def update_project_status_on_task_save(sender, instance, created, **kwargs):
    """
    Automatically update project status when a task is saved.
    
    Rules:
    - If ANY task is 'in_progress', project becomes 'in_progress'
    - If ALL tasks are 'completed', project becomes 'completed'
    - If any task starts (not 'not_started'), project becomes 'in_progress'
    """
    project = instance.project
    all_tasks = project.tasks.all()
    
    if all_tasks.exists():
        # Check if any task is in_progress
        if all_tasks.filter(status='in_progress').exists():
            if project.status != 'in_progress':
                project.status = 'in_progress'
                project.save()
        
        # Check if all tasks are completed
        elif all_tasks.filter(status='completed').count() == all_tasks.count():
            if project.status != 'completed':
                project.status = 'completed'
                project.save()
        
        # If no tasks are in progress and not all completed, check if any started
        elif all_tasks.exclude(status='not_started').exists():
            if project.status == 'not_started':
                project.status = 'in_progress'
                project.save()


@receiver(post_delete, sender=Task)
def update_project_status_on_task_delete(sender, instance, **kwargs):
    """
    Automatically update project status when a task is deleted.
    Recalculates project status based on remaining tasks.
    """
    try:
        project = instance.project
        all_tasks = project.tasks.all()
        
        if not all_tasks.exists():
            # No tasks left, reset to not_started
            if project.status not in ['cancelled', 'on_hold']:
                project.status = 'not_started'
                project.save()
        else:
            # Recalculate based on remaining tasks
            if all_tasks.filter(status='in_progress').exists():
                project.status = 'in_progress'
                project.save()
            elif all_tasks.filter(status='completed').count() == all_tasks.count():
                project.status = 'completed'
                project.save()
            elif all_tasks.exclude(status='not_started').exists():
                if project.status == 'not_started':
                    project.status = 'in_progress'
                    project.save()
    except Project.DoesNotExist:
        pass  # Project was already deleted
