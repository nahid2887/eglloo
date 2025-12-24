from django.db import models
from django.conf import settings
from Project_manager.models import Task
from django.utils import timezone


class TaskTimer(models.Model):
    """
    Model to track employee work time on tasks with start/stop timer.
    Records are saved on a daily basis.
    """
    
    # Relations
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_timers'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='timers'
    )
    
    # Timer fields
    work_date = models.DateField(help_text="Date of work (automatically set)")
    start_time = models.DateTimeField(help_text="When employee started work on this task")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When employee stopped work on this task")
    duration_seconds = models.IntegerField(default=0, help_text="Total time worked in seconds")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="True if timer is currently running")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-work_date', '-start_time']
        indexes = [
            models.Index(fields=['employee', 'work_date']),
            models.Index(fields=['task', 'work_date']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Task Timer"
        verbose_name_plural = "Task Timers"
    
    def __str__(self):
        return f"{self.employee.username} - {self.task.task_name} on {self.work_date}"
    
    def stop_timer(self):
        """Stop the timer and calculate duration"""
        if self.is_active and self.start_time:
            self.end_time = timezone.now()
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
            self.is_active = False
            self.save()
    
    def get_duration_formatted(self):
        """Get duration in human-readable format (HH:MM:SS)"""
        if self.duration_seconds == 0 and self.is_active and self.start_time:
            # Calculate current duration for active timer
            current_duration = int((timezone.now() - self.start_time).total_seconds())
        else:
            current_duration = self.duration_seconds
        
        hours = current_duration // 3600
        minutes = (current_duration % 3600) // 60
        seconds = current_duration % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
