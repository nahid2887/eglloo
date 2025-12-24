#!/usr/bin/env python
"""
Test script for Gantt Chart API
Tests the new /projects/{id}/gantt-chart/ endpoint
"""

import os
import sys
import django
import json

# Add eagleeyeau to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'eagleeyeau'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eagleeyeau.settings')
os.chdir(os.path.join(os.path.dirname(__file__), 'eagleeyeau'))
django.setup()

from django.test import Client
from authentication.models import User
from Project_manager.models import Project

def test_gantt_chart_api():
    """Test the Gantt chart API endpoint"""
    
    # Get a test project
    project = Project.objects.first()
    if not project:
        print("❌ No projects found")
        return
    
    print(f"\n{'='*60}")
    print(f"Testing Gantt Chart API")
    print(f"{'='*60}\n")
    
    # Get an authenticated user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    # Create a test client
    client = Client()
    
    # Make the request
    project_id = project.id
    url = f'/api/project-manager/projects/{project_id}/gantt-chart/'
    
    print(f"📍 Endpoint: GET {url}")
    print(f"📍 Project ID: {project_id}")
    print(f"📍 Project Name: {project.project_name}")
    print(f"📍 Tasks: {project.tasks.count()}\n")
    
    # Simulate authentication by setting user
    response = client.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Response successful!\n")
        
        # Print response structure
        result_data = data.get('data', {})
        
        print(f"Project Details:")
        print(f"  - Project ID: {result_data.get('project_id')}")
        print(f"  - Project Name: {result_data.get('project_name')}")
        print(f"  - Client: {result_data.get('client_name')}")
        print(f"  - Status: {result_data.get('status')}")
        print(f"  - Start Date: {result_data.get('project_start_date')}")
        print(f"  - End Date: {result_data.get('project_end_date')}")
        print(f"  - Total Tasks: {result_data.get('total_tasks')}\n")
        
        print(f"Tasks (Grid View):")
        tasks = result_data.get('tasks', [])
        for i, task in enumerate(tasks, 1):
            print(f"\n  Task {i}:")
            print(f"    ID: {task.get('id')}")
            print(f"    Name: {task.get('task_name')}")
            print(f"    Room: {task.get('room')}")
            print(f"    Timeline: {task.get('start_date')} → {task.get('due_date')}")
            print(f"    Status: {task.get('status')}")
            print(f"    Priority: {task.get('priority')}")
            print(f"    Assigned: {task.get('assigned_employee_name') or 'Unassigned'}")
        
        print(f"\n{'='*60}")
        print("📊 Perfect for Gantt/Timeline Visualization!")
        print(f"{'='*60}\n")
        
        # Print JSON for reference
        print("Full JSON Response:")
        print(json.dumps(data, indent=2, default=str))
        
    elif response.status_code == 404:
        print("❌ Project not found (404)")
    elif response.status_code == 403:
        print("❌ Permission denied (403)")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.content)

if __name__ == '__main__':
    test_gantt_chart_api()
