#!/usr/bin/env python
"""
Test script to verify task and project status updates
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eagleeyeau.settings')
sys.path.insert(0, '/c/eagleeyeau/eagleeyeau')
django.setup()

from emopye.models import TaskTimer
from Project_manager.models import Task, Project
from django.utils import timezone

print("=" * 80)
print("TEST: Task Status Update - Real Scenario")
print("=" * 80)

# Get the timer
timer = TaskTimer.objects.get(id=9)
task = timer.task
project = task.project

print("\n1️⃣  INITIAL STATE:")
print(f"   Timer ID: {timer.id}")
print(f"   Timer is_active: {timer.is_active}")
print(f"   Task Status: {task.status}")
print(f"   Project Status: {project.status}")

# Simulate updating task to 'completed'
print("\n2️⃣  UPDATING TASK STATUS TO 'completed' (PATCH request simulation):")
old_status = task.status
new_status = 'completed'
task.status = new_status
task.save()
print(f"   Task Status AFTER save: {task.status}")

# Update project status based on task statuses
old_project_status = project.status
all_tasks = project.tasks.all()

print(f"\n3️⃣  PROJECT STATUS LOGIC (checking all {all_tasks.count()} tasks):")
print(f"   All tasks statuses: {list(all_tasks.values_list('task_name', 'status'))}")

if all_tasks.exists():
    in_progress_count = all_tasks.filter(status='in_progress').count()
    completed_count = all_tasks.filter(status='completed').count()
    
    print(f"   - In Progress tasks: {in_progress_count}")
    print(f"   - Completed tasks: {completed_count}")
    print(f"   - Total tasks: {all_tasks.count()}")
    
    if in_progress_count > 0:
        print(f"   → Action: Found {in_progress_count} in_progress tasks")
        if project.status != 'in_progress':
            project.status = 'in_progress'
            project.save()
            print(f"   → Updated project to 'in_progress'")
    
    elif completed_count == all_tasks.count():
        print(f"   → Action: All {completed_count} tasks are completed")
        if project.status != 'completed':
            project.status = 'completed'
            project.save()
            print(f"   → Updated project to 'completed'")
    
    elif all_tasks.exclude(status='not_started').count() > 0:
        print(f"   → Action: Some tasks have been started")
        if project.status == 'not_started':
            project.status = 'in_progress'
            project.save()
            print(f"   → Updated project to 'in_progress'")

print(f"\n4️⃣  FINAL STATE AFTER UPDATE:")
task.refresh_from_db()
project.refresh_from_db()
print(f"   Task Status: {task.status}")
print(f"   Project Status: {project.status}")
print(f"   Project Status Changed: {old_project_status != project.status}")

print("\n5️⃣  DAILY-SUMMARY API (when called):")
print(f"   Timer is_active: {timer.is_active}")
print(f"   Check: if timer.is_active and project.status == 'not_started'")
print(f"   Result: {timer.is_active and project.status == 'not_started'}")
if timer.is_active and project.status == 'not_started':
    print("   → Would auto-update project to 'in_progress'")
else:
    print("   → Project status will NOT change (already 'completed')")
    print(f"   → Final project status shown in API: {project.status}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETED")
print("=" * 80)
