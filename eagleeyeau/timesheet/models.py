from django.db import models
from django.utils import timezone
from authentication.models import User
from datetime import datetime, timedelta


class TimeEntry(models.Model):
    """Model for employee time entries"""
    
    ATTENDANCE_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField(default=timezone.localdate)
    
    # Start and End times
    entry_time = models.TimeField(null=True, blank=True, help_text="Clock in time")
    exit_time = models.TimeField(null=True, blank=True, help_text="Clock out time")
    
    # Calculated fields
    total_working_time = models.DurationField(null=True, blank=True, help_text="Total hours worked")
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='Absent')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-entry_time']
        unique_together = ['user', 'date']
        verbose_name = 'Time Entry'
        verbose_name_plural = 'Time Entries'
    
    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.attendance}"
    
    def calculate_working_time(self):
        """Calculate total working time between entry and exit"""
        if self.entry_time and self.exit_time:
            # Create datetime objects for calculation
            today = timezone.now().date()
            entry_datetime = datetime.combine(today, self.entry_time)
            exit_datetime = datetime.combine(today, self.exit_time)
            
            # Handle case where exit time is before entry time (next day scenario)
            if exit_datetime < entry_datetime:
                exit_datetime += timedelta(days=1)
            
            # Calculate duration
            duration = exit_datetime - entry_datetime
            self.total_working_time = duration
            
            # Auto-set attendance based on working time
            hours_worked = duration.total_seconds() / 3600
            if hours_worked >= 6:  # 6+ hours = Present
                self.attendance = 'Present'
            elif hours_worked >= 4:  # 4-6 hours = Half Day
                self.attendance = 'Half Day'
            else:
                self.attendance = 'Absent'
            
            return duration
        return None
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate working time"""
        self.calculate_working_time()
        super().save(*args, **kwargs)
    
    def get_working_hours(self):
        """Return working time in hours and minutes format"""
        if self.total_working_time:
            total_seconds = int(self.total_working_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    
    @staticmethod
    def get_weekly_hours(user, start_date=None, end_date=None):
        """Get total hours for a week"""
        if not start_date:
            # Get current week (Monday to Sunday)
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        if not end_date:
            end_date = start_date + timedelta(days=6)
        
        entries = TimeEntry.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        total_duration = timedelta()
        for entry in entries:
            if entry.total_working_time:
                total_duration += entry.total_working_time
        
        total_seconds = int(total_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        return {
            'total_hours': hours,
            'total_minutes': minutes,
            'formatted': f"{hours}h {minutes}m",
            'entries': entries
        }
