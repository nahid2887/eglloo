from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db import models
from datetime import timedelta
from eagleeyeau.response_formatter import format_response
from Project_manager.models import Task, Project
from .serializers import (
    EmployeeAssignedTaskSerializer,
    EmployeeTaskStatsSerializer,
    EmployeeAssignedProjectSerializer,
)


# ====================== PERMISSIONS ======================
class IsEmployee(permissions.BasePermission):
    """Allow only Employee role users"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'Employee'
        )


# ====================== EMPLOYEE ASSIGNED TASKS API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get employee assigned tasks with statistics and pagination",
    operation_description="""
    API endpoint for Employee to view all their assigned tasks with statistics.
    
    This endpoint returns:
    - Total count of assigned tasks
    - Completed tasks count
    - Due tasks (due date has passed) count
    - Upcoming tasks (due within 7 days) count
    - In-progress tasks count
    - Not started tasks count
    - Paginated list of all assigned tasks with project details
    
    Query Parameters:
    - status: Filter by task status (not_started, in_progress, completed, blocked)
    - priority: Filter by priority (low, medium, high)
    - project_id: Filter by specific project
    - search: Search in task name, description, project name, or room name
    - page: Page number for pagination (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    
    Returns:
    - Task statistics summary
    - Paginated list of assigned tasks with full project information
    - Pagination metadata (count, next, previous, page info)
    
    Only the authenticated employee can view their own tasks.
    """,
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by task status (not_started, in_progress, completed, blocked)',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'priority',
            openapi.IN_QUERY,
            description='Filter by priority (low, medium, high)',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'project_id',
            openapi.IN_QUERY,
            description='Filter by specific project ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description='Search by task name, description, project name, or room name',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description='Page number for pagination (default: 1)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description='Number of items per page (default: 10, max: 100)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Employee assigned tasks retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'statistics': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'completed_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'due_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'upcoming_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'in_progress_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'not_started_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'pagination': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'next': openapi.Schema(type=openapi.TYPE_STRING),
                                    'previous': openapi.Schema(type=openapi.TYPE_STRING),
                                    'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'tasks': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        }
                    )
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required"),
        403: openapi.Response(description="Forbidden - Only Employee role can access this"),
    },
    tags=['Employee - Tasks']
)
def get_employee_assigned_tasks(request):
    """
    API endpoint for Employee to view all their assigned tasks with pagination.
    
    Endpoint: GET /api/employee/assigned-tasks/
    
    Only returns tasks assigned to the logged-in employee.
    Includes task statistics (total, completed, due, upcoming, etc.)
    Supports filtering, searching, and pagination.
    
    Query Parameters:
    - status: Filter by task status (not_started, in_progress, completed, blocked)
    - priority: Filter by priority (low, medium, high)
    - project_id: Filter by specific project
    - search: Search in task name, description, project name, or room name
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    
    Returns paginated task list with project details for each task.
    """
    try:
        from django.db.models import Q
        
        current_user = request.user
        
        # Get all tasks assigned to the current employee
        tasks = Task.objects.filter(assigned_employee=current_user).select_related(
            'project', 'project__created_by', 'created_by'
        )
        
        # Apply filters
        status_filter = request.query_params.get('status', '').strip()
        priority_filter = request.query_params.get('priority', '').strip()
        project_id_filter = request.query_params.get('project_id', '').strip()
        search_query = request.query_params.get('search', '').strip()
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if project_id_filter:
            tasks = tasks.filter(project_id=project_id_filter)
        
        # Enhanced search functionality
        if search_query:
            tasks = tasks.filter(
                Q(task_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(project__project_name__icontains=search_query) |
                Q(room__icontains=search_query)
            )
        
        # Order by priority and due date
        tasks = tasks.order_by('priority', 'due_date')
        
        # Calculate statistics (before pagination)
        all_tasks = Task.objects.filter(assigned_employee=current_user)
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=7)
        
        stats = {
            'total_tasks': all_tasks.count(),
            'completed_tasks': all_tasks.filter(status='completed').count(),
            'due_tasks': all_tasks.filter(due_date__lt=today).exclude(status='completed').count(),
            'upcoming_tasks': all_tasks.filter(due_date__lte=upcoming_date, due_date__gte=today).count(),
            'in_progress_tasks': all_tasks.filter(status='in_progress').count(),
            'not_started_tasks': all_tasks.filter(status='not_started').count(),
        }
        
        # Pagination
        page_size = request.query_params.get('page_size', 10)
        try:
            page_size = min(int(page_size), 100)  # Max 100 items per page
            page_size = max(page_size, 1)  # Min 1 item per page
        except (ValueError, TypeError):
            page_size = 10
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_tasks = paginator.paginate_queryset(tasks, request)
        
        # Serialize data
        tasks_serializer = EmployeeAssignedTaskSerializer(paginated_tasks, many=True)
        stats_serializer = EmployeeTaskStatsSerializer(stats)
        
        # Get pagination info
        page_number = request.query_params.get('page', 1)
        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            page_number = 1
        
        total_count = tasks.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        response_data = format_response(
            success=True,
            message=f"Retrieved {paginated_tasks.__len__()} assigned tasks for employee {current_user.get_full_name()}",
            data={
                'employee': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'full_name': current_user.get_full_name(),
                    'email': current_user.email,
                },
                'statistics': stats_serializer.data,
                'pagination': {
                    'count': total_count,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'current_page': page_number,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                'tasks': tasks_serializer.data,
            }
        )
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving assigned tasks: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE SINGLE ASSIGNED TASK API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get single assigned task details",
    operation_description="""
    API endpoint for Employee to view details of a single assigned task.
    
    This endpoint returns complete details of a specific task assigned to the current employee.
    
    Endpoint: GET /api/employee/assigned-tasks/{task_id}/
    
    Path Parameters:
    - task_id: ID of the task to retrieve
    
    Returns:
    - Complete task details with all information
    - Project information
    - Employee assignment details
    - Task status and priority
    - Timestamps and other metadata
    
    Only the employee to whom the task is assigned can view it.
    """,
    responses={
        200: openapi.Response(
            description="Task details retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required"),
        403: openapi.Response(description="Forbidden - You cannot view this task"),
        404: openapi.Response(description="Task not found"),
    },
    tags=['Employee - Tasks']
)
def get_single_assigned_task(request, task_id):
    """
    API endpoint to get a single task assigned to the employee.
    
    Endpoint: GET /api/employee/assigned-tasks/{task_id}/
    
    Only returns the task if it's assigned to the current employee.
    Includes all task details, project information, and timestamps.
    """
    try:
        current_user = request.user
        
        # Get the task and verify it belongs to the current employee
        task = Task.objects.select_related(
            'project', 'project__created_by', 'created_by', 'assigned_employee'
        ).get(id=task_id, assigned_employee=current_user)
        
        # Serialize the task
        serializer = EmployeeAssignedTaskSerializer(task)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved task details for task ID {task_id}",
                data={
                    'task': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Task.DoesNotExist:
        return Response(
            format_response(
                success=False,
                message=f"Task with ID {task_id} not found or not assigned to you",
                data=None
            ),
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving task details: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH', 'POST'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Update task status",
    operation_description="""
    API endpoint for Employee to update the status of their assigned tasks.
    
    Employees can only update the status of tasks assigned to them.
    
    **Automatic Project Status Updates:**
    - If ANY task is set to 'in_progress', the project status automatically becomes 'in_progress'
    - If ALL tasks are 'completed', the project status automatically becomes 'completed'
    - If any task starts (not 'not_started'), and project is 'not_started', it becomes 'in_progress'
    
    Allowed task status values:
    - 'not_started': Task hasn't started yet
    - 'in_progress': Task is currently being worked on (triggers project to 'in_progress')
    - 'completed': Task is finished (if all tasks completed, project becomes 'completed')
    - 'blocked': Task is blocked/delayed
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['task_id', 'status'],
        properties={
            'task_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the task to update'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['not_started', 'in_progress', 'completed', 'blocked'], description='New task status'),
        },
        example={
            'task_id': 5,
            'status': 'in_progress'
        }
    ),
    responses={
        200: openapi.Response(description="Task status updated successfully"),
        400: openapi.Response(description="Invalid task ID or status"),
        403: openapi.Response(description="Forbidden - Task not assigned to you"),
        404: openapi.Response(description="Task not found"),
    },
    tags=['Employee - Tasks']
)
def update_employee_task_status(request):
    """
    API endpoint for Employee to update task status.
    
    Endpoint: PATCH /api/employee/update-task-status/
    
    Only employees can update the status of tasks assigned to them.
    """
    try:
        task_id = request.data.get('task_id')
        new_status = request.data.get('status')
        
        if not task_id or not new_status:
            return Response(
                format_response(
                    success=False,
                    message="task_id and status are required",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message=f"Task with ID {task_id} not found",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if task is assigned to current employee
        if task.assigned_employee != request.user:
            return Response(
                format_response(
                    success=False,
                    message="This task is not assigned to you",
                    data=None
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate status
        valid_statuses = ['not_started', 'in_progress', 'completed', 'blocked']
        if new_status not in valid_statuses:
            return Response(
                format_response(
                    success=False,
                    message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update task status
        old_status = task.status
        task.status = new_status
        task.save()
        
        # Automatically update project status based on tasks
        project = task.project
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
        
        serializer = EmployeeAssignedTaskSerializer(task)
        
        return Response(
            format_response(
                success=True,
                message=f"Task '{task.task_name}' status updated from '{old_status}' to '{new_status}'. Project status: '{project.status}'",
                data={
                    'task': serializer.data,
                    'project_status': project.status,
                    'project_id': project.id,
                    'project_name': project.project_name
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error updating task status: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE ASSIGNED PROJECTS API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get employee assigned projects",
    operation_description="""
    API endpoint for Employee to view all projects they have tasks assigned to.
    
    This endpoint returns:
    - All projects where the employee has assigned tasks
    - Progress percentage (based on completed tasks vs total tasks)
    - Total project tasks count
    - Employee's assigned tasks count per project
    - Completed tasks count
    - Creation date and deadline
    - Deadline status (days left to deliver)
    - Project details (name, client, description, rooms, etc.)
    
    Query Parameters:
    - status: Filter by project status (not_started, in_progress, completed, on_hold, cancelled)
    - search: Search in project name or client name
    
    Returns:
    - Statistics: total_projects, completed_projects, due_projects, cancelled_projects
    - List of all projects with progress and task information
    
    Example Response:
    {
        "success": true,
        "message": "Retrieved 5 assigned projects",
        "data": {
            "statistics": {
                "total_projects": 5,
                "completed_projects": 2,
                "due_projects": 2,
                "cancelled_projects": 1
            },
            "projects": [
                {
                    "id": 6,
                    "project_name": "Home Renovation",
                    "client_name": "John Doe",
                    "description": "Design the layout...",
                    "status": "in_progress",
                    "progress": 35,
                    "creating_date": "2025-04-20",
                    "start_date": "2025-04-20",
                    "end_date": "2025-05-23",
                    "deadline_status": "20 days left to deliver",
                    "total_tasks": 5,
                    "assigned_tasks_count": 3,
                    "completed_tasks": 1,
                    "created_by_name": "Project Manager"
                }
            ]
        }
    }
    """,
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by project status (not_started, in_progress, completed, on_hold, cancelled)',
            type=openapi.TYPE_STRING,
            enum=['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled'],
            required=False
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description='Search in project name or client name',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description='Page number for pagination (default: 1)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description='Number of items per page (default: 10, max: 100)',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'statistics': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_projects': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'completed_projects': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'due_projects': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'cancelled_projects': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'pagination': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'next': openapi.Schema(type=openapi.TYPE_STRING),
                                    'previous': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            ),
                            'projects': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        }
                    )
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required"),
        403: openapi.Response(description="Forbidden - Only Employee role can access this"),
    },
    tags=['Employee - Projects']
)
def get_employee_assigned_projects(request):
    """
    API endpoint for Employee to view all projects they have tasks assigned to with pagination.
    Shows project progress, task counts, deadlines, and other details.
    
    Endpoint: GET /api/employee/assigned-projects/
    
    Query Parameters:
    - status: Filter by project status (not_started, in_progress, completed, on_hold, cancelled)
    - search: Search in project name or client name
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    
    Returns paginated project list with statistics.
    """
    try:
        from django.db.models import Q
        
        employee = request.user
        
        # Get all projects where employee has assigned tasks
        projects = Project.objects.filter(
            tasks__assigned_employee=employee
        ).distinct().order_by('-creating_date')
        
        # Apply status filter
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            projects = projects.filter(status=status_filter)
        
        # Apply search filter
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            projects = projects.filter(
                Q(project_name__icontains=search_query) |
                Q(client_name__icontains=search_query)
            )
        
        # Calculate statistics (before pagination)
        total_projects = projects.count()
        completed_projects = projects.filter(status='completed').count()
        due_projects = projects.filter(
            end_date__lt=timezone.now().date(),
            status__in=['not_started', 'in_progress', 'on_hold']
        ).count()
        cancelled_projects = projects.filter(status='cancelled').count()
        
        # Pagination
        page_size = request.query_params.get('page_size', 10)
        try:
            page_size = min(int(page_size), 100)  # Max 100 items per page
            page_size = max(page_size, 1)  # Min 1 item per page
        except (ValueError, TypeError):
            page_size = 10
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_projects = paginator.paginate_queryset(projects, request)
        
        # Serialize the data
        serializer = EmployeeAssignedProjectSerializer(
            paginated_projects,
            many=True,
            context={'employee': employee}
        )
        
        # Get pagination info
        page_number = request.query_params.get('page', 1)
        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            page_number = 1
        
        total_pages = (total_projects + page_size - 1) // page_size
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {paginated_projects.__len__()} assigned projects",
                data={
                    'statistics': {
                        'total_projects': total_projects,
                        'completed_projects': completed_projects,
                        'due_projects': due_projects,
                        'cancelled_projects': cancelled_projects,
                    },
                    'pagination': {
                        'count': total_projects,
                        'page_size': page_size,
                        'total_pages': total_pages,
                        'current_page': page_number,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                    },
                    'projects': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving assigned projects: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE SINGLE ASSIGNED PROJECT API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get single assigned project details",
    operation_description="""
    API endpoint for Employee to view details of a single assigned project.
    
    This endpoint returns complete details of a specific project where the employee has assigned tasks.
    
    Endpoint: GET /api/employee/assigned-projects/{project_id}/
    
    Path Parameters:
    - project_id: ID of the project to retrieve
    
    Returns:
    - Complete project details
    - Project status and timeline
    - Task count statistics for this project
    - Client information
    - Project description and other metadata
    
    Only projects where the employee has assigned tasks can be viewed.
    """,
    responses={
        200: openapi.Response(
            description="Project details retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required"),
        403: openapi.Response(description="Forbidden - You have no tasks in this project"),
        404: openapi.Response(description="Project not found"),
    },
    tags=['Employee - Projects']
)
def get_single_assigned_project(request, project_id):
    """
    API endpoint to get a single project assigned to the employee.
    
    Endpoint: GET /api/employee/assigned-projects/{project_id}/
    
    Only returns the project if the employee has assigned tasks in it.
    Includes complete project details and statistics.
    """
    try:
        employee = request.user
        
        # Get the project and verify employee has tasks in it
        # Using filter().distinct().first() instead of get() to handle multiple tasks
        project = Project.objects.filter(
            id=project_id, 
            tasks__assigned_employee=employee
        ).distinct().first()
        
        # Check if project exists and employee has tasks in it
        if not project:
            return Response(
                format_response(
                    success=False,
                    message=f"Project with ID {project_id} not found or you have no tasks in this project",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get task statistics for this project assigned to the employee
        employee_tasks = Task.objects.filter(
            project=project,
            assigned_employee=employee
        )
        
        task_stats = {
            'total_tasks': employee_tasks.count(),
            'completed_tasks': employee_tasks.filter(status='completed').count(),
            'in_progress_tasks': employee_tasks.filter(status='in_progress').count(),
            'not_started_tasks': employee_tasks.filter(status='not_started').count(),
            'due_tasks': employee_tasks.filter(
                due_date__lt=timezone.now().date()
            ).exclude(status='completed').count(),
        }
        
        # Serialize the project
        serializer = EmployeeAssignedProjectSerializer(
            project,
            context={'employee': employee}
        )
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved project details for project ID {project_id}",
                data={
                    'project': serializer.data,
                    'task_statistics': task_stats
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving project details: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE PROJECT TASKS API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get all tasks for a specific project",
    operation_description="""
    API endpoint for Employee to view all tasks for a specific project.
    
    This endpoint returns all tasks for a given project ID that are assigned to the current employee.
    
    Endpoint: GET /api/employee/projects/{project_id}/tasks/
    
    Query Parameters:
    - status: Filter by task status (not_started, in_progress, completed, blocked)
    - priority: Filter by priority (low, medium, high)
    
    Returns:
    - Project details (name, status, description, deadline)
    - Total tasks count for this project (assigned to you)
    - Completed tasks count
    - In-progress tasks count
    - List of all tasks with details
    
    Example Response:
    {
        "success": true,
        "message": "Retrieved 5 tasks for project 'Home Renovation'",
        "data": {
            "project": {
                "id": 6,
                "project_name": "Home Renovation",
                "client_name": "John Doe",
                "description": "Complete home renovation project",
                "status": "in_progress",
                "start_date": "2025-04-20",
                "end_date": "2025-05-23",
                "deadline_status": "20 days left"
            },
            "statistics": {
                "total_tasks": 5,
                "completed_tasks": 2,
                "in_progress_tasks": 2,
                "not_started_tasks": 1
            },
            "tasks": [
                {
                    "id": 12,
                    "task_name": "Kitchen Design",
                    "description": "Design kitchen layout",
                    "status": "in_progress",
                    "priority": "high",
                    "start_date": "2025-04-20",
                    "due_date": "2025-04-25",
                    "estimated_hours": 40,
                    "progress_percentage": 50
                }
            ]
        }
    }
    """,
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by task status',
            type=openapi.TYPE_STRING,
            enum=['not_started', 'in_progress', 'completed', 'blocked']
        ),
        openapi.Parameter(
            'priority',
            openapi.IN_QUERY,
            description='Filter by priority',
            type=openapi.TYPE_STRING,
            enum=['low', 'medium', 'high']
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Retrieved 5 tasks"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'project': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'statistics': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'completed_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'in_progress_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'not_started_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'tasks': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        }
                    )
                }
            )
        ),
        403: openapi.Response(description="Forbidden - No tasks assigned to you in this project"),
        404: openapi.Response(description="Not Found - Project not found"),
    },
    tags=['Employee - Projects']
)
def get_employee_project_tasks(request, project_id):
    """
    API endpoint for Employee to view all their tasks for a specific project.
    """
    try:
        employee = request.user
        
        # Get the project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message=f"Project with ID {project_id} not found",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all tasks assigned to this employee for this project
        tasks = Task.objects.filter(
            project=project,
            assigned_employee=employee
        ).order_by('start_date', 'due_date')
        
        # Check if employee has any tasks in this project
        if not tasks.exists():
            return Response(
                format_response(
                    success=False,
                    message=f"You don't have any tasks assigned in project '{project.project_name}'",
                    data=None
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Apply filters
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        priority_filter = request.query_params.get('priority', '').strip()
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        # Calculate statistics
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress_tasks = tasks.filter(status='in_progress').count()
        not_started_tasks = tasks.filter(status='not_started').count()
        
        # Serialize tasks
        task_serializer = EmployeeAssignedTaskSerializer(tasks, many=True)
        
        # Calculate deadline status
        if project.end_date:
            today = timezone.now().date()
            days_left = (project.end_date - today).days
            
            if days_left < 0:
                deadline_status = f"{abs(days_left)} days overdue"
            elif days_left == 0:
                deadline_status = "Due today"
            else:
                deadline_status = f"{days_left} days left"
        else:
            deadline_status = "No deadline set"
        
        # Prepare project details
        project_data = {
            'id': project.id,
            'project_name': project.project_name,
            'client_name': project.client_name,
            'description': project.description,
            'status': project.status,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
            'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
            'deadline_status': deadline_status,
            'rooms': project.rooms,
            'created_by_name': f"{project.created_by.first_name} {project.created_by.last_name}" if project.created_by else "Unknown"
        }
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {total_tasks} tasks for project '{project.project_name}'",
                data={
                    'project': project_data,
                    'statistics': {
                        'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'in_progress_tasks': in_progress_tasks,
                        'not_started_tasks': not_started_tasks,
                    },
                    'tasks': task_serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving project tasks: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE UPDATE TASK STATUS (RESTful) ======================
@api_view(['PATCH', 'POST'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Update task status (RESTful endpoint)",
    operation_description="""
    RESTful API endpoint for Employee to update the status of their assigned task.
    
    Employees can only update the status of tasks assigned to them.
    
    **Automatic Project Status Updates:**
    - If ANY task is set to 'in_progress', the project status automatically becomes 'in_progress'
    - If ALL tasks are 'completed', the project status automatically becomes 'completed'
    - If any task starts (not 'not_started'), and project is 'not_started', it becomes 'in_progress'
    
    Allowed task status values:
    - 'not_started': Task hasn't started yet
    - 'in_progress': Task is currently being worked on (triggers project to 'in_progress')
    - 'completed': Task is finished (if all tasks completed, project becomes 'completed')
    - 'blocked': Task is blocked/delayed
    
    Example:
    PATCH /api/employee/tasks/5/status/
    {
        "status": "in_progress"
    }
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['status'],
        properties={
            'status': openapi.Schema(
                type=openapi.TYPE_STRING, 
                enum=['not_started', 'in_progress', 'completed', 'blocked'], 
                description='New task status'
            ),
        },
        example={
            'status': 'in_progress'
        }
    ),
    responses={
        200: openapi.Response(
            description="Task status updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'task': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'project_status': openapi.Schema(type=openapi.TYPE_STRING),
                            'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'project_name': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: openapi.Response(description="Invalid status value"),
        403: openapi.Response(description="Forbidden - Task not assigned to you"),
        404: openapi.Response(description="Task not found"),
    },
    tags=['Employee - Tasks']
)
def update_task_status(request, task_id):
    """
    RESTful API endpoint for Employee to update task status.
    
    Endpoint: PATCH /api/employee/tasks/{task_id}/status/
    
    Only employees can update the status of tasks assigned to them.
    Automatically updates project status based on task statuses.
    """
    try:
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                format_response(
                    success=False,
                    message="status field is required",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message=f"Task with ID {task_id} not found",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if task is assigned to current employee
        if task.assigned_employee != request.user:
            return Response(
                format_response(
                    success=False,
                    message="This task is not assigned to you. You can only update tasks assigned to you.",
                    data=None
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate status
        valid_statuses = ['not_started', 'in_progress', 'completed', 'blocked']
        if new_status not in valid_statuses:
            return Response(
                format_response(
                    success=False,
                    message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update task status
        old_status = task.status
        task.status = new_status
        task.save()
        
        # Automatically update project status based on tasks
        project = task.project
        all_tasks = project.tasks.all()
        old_project_status = project.status
        
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
        
        serializer = EmployeeAssignedTaskSerializer(task)
        
        # Build message
        message = f"Task '{task.task_name}' status updated from '{old_status}' to '{new_status}'."
        if old_project_status != project.status:
            message += f" Project '{project.project_name}' status automatically updated from '{old_project_status}' to '{project.status}'."
        
        return Response(
            format_response(
                success=True,
                message=message,
                data={
                    'task': serializer.data,
                    'project_status': project.status,
                    'project_status_changed': old_project_status != project.status,
                    'project_id': project.id,
                    'project_name': project.project_name
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error updating task status: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE TASK SCHEDULE API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get employee task schedule (sorted by date)",
    operation_description="""
    API endpoint for Employee to view their task schedule with start_date and end_date (due_date).
    
    Returns tasks sorted by start_date (earliest first), then by due_date.
    
    This endpoint is perfect for calendar views and scheduling dashboards.
    
    Query Parameters:
    - start_date: Filter tasks starting from this date (YYYY-MM-DD)
    - end_date: Filter tasks ending before this date (YYYY-MM-DD)
    - status: Filter by task status (not_started, in_progress, completed, blocked)
    
    Returns:
    - List of all assigned tasks sorted by date (start_date, then due_date)
    - Each task includes project info, dates, status, and priority
    
    Example:
    - /api/employee/task-schedule/
    - /api/employee/task-schedule/?start_date=2025-12-01&end_date=2025-12-31
    - /api/employee/task-schedule/?status=in_progress
    """,
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description='Filter tasks with start_date on or after this date (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description='Filter tasks with due_date on or before this date (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by task status',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Task schedule retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'tasks': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'task_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                        'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                                        'priority': openapi.Schema(type=openapi.TYPE_STRING),
                                        'project_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    }
                                )
                            )
                        }
                    )
                }
            )
        ),
    },
    tags=['Employee - Tasks']
)
def get_employee_task_schedule(request):
    """
    API endpoint for Employee to view their task schedule sorted by dates.
    
    Endpoint: GET /api/employee/task-schedule/
    
    Returns tasks sorted chronologically by start_date, then due_date.
    Perfect for calendar and timeline views.
    
    Query Parameters:
    - start_date: Filter tasks starting from date
    - end_date: Filter tasks ending before date
    - status: Filter by status
    """
    try:
        from datetime import datetime
        current_user = request.user
        
        # Get all tasks assigned to the current employee
        tasks = Task.objects.filter(assigned_employee=current_user).select_related(
            'project', 'created_by'
        )
        
        # Apply date filters
        start_date_filter = request.query_params.get('start_date', '').strip()
        end_date_filter = request.query_params.get('end_date', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        
        if start_date_filter:
            try:
                start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
                tasks = tasks.filter(start_date__gte=start_date)
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid start_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date_filter:
            try:
                end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()
                tasks = tasks.filter(due_date__lte=end_date)
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid end_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        # Sort by start_date first, then due_date
        tasks = tasks.order_by('start_date', 'due_date')
        
        # Serialize data with date focus
        task_schedule = []
        for task in tasks:
            task_schedule.append({
                'id': task.id,
                'task_name': task.task_name,
                'description': task.description,
                'start_date': task.start_date,
                'due_date': task.due_date,
                'status': task.status,
                'priority': task.priority,
                'phase': task.phase,
                'room': task.room,
                'project_id': task.project.id,
                'project_name': task.project.project_name,
                'client_name': task.project.client_name,
                'created_at': task.created_at,
                'updated_at': task.updated_at,
            })
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {len(task_schedule)} tasks in schedule for {current_user.get_full_name()}",
                data={
                    'employee': {
                        'id': current_user.id,
                        'username': current_user.username,
                        'full_name': current_user.get_full_name(),
                        'email': current_user.email,
                    },
                    'filters_applied': {
                        'start_date': start_date_filter if start_date_filter else None,
                        'end_date': end_date_filter if end_date_filter else None,
                        'status': status_filter if status_filter else None,
                    },
                    'total_tasks': len(task_schedule),
                    'tasks': task_schedule,
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving task schedule: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== TASK TIMER API ======================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Start/Stop task timer (toggle)",
    operation_description="""
    Single API endpoint to start or stop work timer for a task.
    
    How it works:
    - If no active timer exists for this task today → START new timer
    - If active timer exists for this task today → STOP the timer and save duration
    - Employee can ONLY have ONE active timer at a time (across all projects)
    - Cannot start a new project timer if another project timer is already active
    
    The timer tracks time spent on a task on a daily basis.
    Each day creates a new timer record.
    
    Request Body:
    - task_id: ID of the task to track time for (REQUIRED)
    - project_id: ID of the project this task belongs to (REQUIRED)
    
    IMPORTANT RULES:
    1. Both task_id and project_id are REQUIRED
    2. Task must belong to the specified project
    3. Only ONE active timer allowed per day (cannot work on multiple projects simultaneously)
    4. Must stop current timer before starting a new project timer
    
    Returns:
    - Timer status (started/stopped)
    - Current timer details
    - Total time worked today (if timer stopped)
    - Active timer info (if trying to start another project timer)
    
    Example Request Body:
    {
        "task_id": 5,
        "project_id": 3
    }
    
    Scenarios:
    1. First call with Project A task → Starts timer
    2. Second call with same task → Stops timer and shows duration
    3. Third call with Project B task (while Project A timer active) → REJECTED with error
    4. After stopping Project A, call with Project B → Starts timer for Project B
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['task_id', 'project_id'],
        properties={
            'task_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the task to track time for (REQUIRED)',
                example=5
            ),
            'project_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the project this task belongs to (REQUIRED)',
                example=3
            ),
        },
        example={
            'task_id': 5,
            'project_id': 3
        }
    ),
    responses={
        200: openapi.Response(
            description="Timer toggled successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Timer started for task 'Kitchen Design' in project 'Office Renovation'"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'action': openapi.Schema(
                                type=openapi.TYPE_STRING, 
                                description='started or stopped',
                                example='started'
                            ),
                            'timer': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                    'task_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                                    'task_name': openapi.Schema(type=openapi.TYPE_STRING, example='Kitchen Design'),
                                    'project_name': openapi.Schema(type=openapi.TYPE_STRING, example='Office Renovation'),
                                    'work_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='2025-11-20'),
                                    'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', example='2025-11-20T10:00:00Z'),
                                    'end_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', nullable=True, example=None),
                                    'duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                    'duration_formatted': openapi.Schema(type=openapi.TYPE_STRING, example='00:00:00'),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                }
                            ),
                            'project_info': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                    'project_name': openapi.Schema(type=openapi.TYPE_STRING, example='Office Renovation'),
                                }
                            ),
                        }
                    )
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request - Missing parameters or timer conflict",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Cannot start timer. You already have an active timer for 'Task Name' in project 'Project Name'. Please stop that timer first."
                    ),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'active_timer_info': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'project_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'task_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'started_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                                }
                            )
                        }
                    )
                }
            )
        ),
        404: openapi.Response(description="Not Found - Task not found, not assigned to you, or doesn't belong to project"),
    },
    tags=['Employee - Task Timer']
)
def toggle_task_timer(request):
    """
    Toggle task timer - Start if not running, Stop if running.
    
    Endpoint: POST /api/employee/timer/toggle/
    
    Request Body:
    {
        "task_id": 5,
        "project_id": 3
    }
    
    Rules:
    - Both task_id and project_id are required
    - task must belong to the specified project
    - Employee can only have ONE active timer at a time across ALL projects
    - Cannot start a new project timer if another project timer is already active
    
    Returns timer status and duration.
    """
    try:
        from .models import TaskTimer
        from .serializers import TaskTimerSerializer
        
        current_user = request.user
        task_id = request.data.get('task_id')
        project_id = request.data.get('project_id')
        
        # Validate required parameters
        if not task_id or not project_id:
            return Response(
                format_response(
                    success=False,
                    message="Both task_id and project_id are required",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if project exists and is accessible
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message="Project not found",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if task exists and is assigned to employee
        try:
            task = Task.objects.get(id=task_id, assigned_employee=current_user, project=project)
        except Task.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message="Task not found or not assigned to you, or does not belong to this project",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get today's date
        today = timezone.now().date()
        
        # Check if there's an active timer for this task today
        active_timer_same_task = TaskTimer.objects.filter(
            employee=current_user,
            task=task,
            work_date=today,
            is_active=True
        ).first()
        
        if active_timer_same_task:
            # STOP the timer for this task
            active_timer_same_task.stop_timer()
            serializer = TaskTimerSerializer(active_timer_same_task)
            
            # Calculate total time worked today for this task
            total_today = TaskTimer.objects.filter(
                employee=current_user,
                task=task,
                work_date=today
            ).aggregate(total=models.Sum('duration_seconds'))['total'] or 0
            
            hours = total_today // 3600
            minutes = (total_today % 3600) // 60
            seconds = total_today % 60
            total_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            return Response(
                format_response(
                    success=True,
                    message=f"Timer stopped for task '{task.task_name}'",
                    data={
                        'action': 'stopped',
                        'timer': serializer.data,
                        'total_time_today': {
                            'seconds': total_today,
                            'formatted': total_formatted
                        }
                    }
                ),
                status=status.HTTP_200_OK
            )
        else:
            # Check if there's ANY active timer for a different project
            active_timer_other_project = TaskTimer.objects.filter(
                employee=current_user,
                work_date=today,
                is_active=True
            ).exclude(task__project=project).first()
            
            if active_timer_other_project:
                other_project_name = active_timer_other_project.task.project.project_name
                other_task_name = active_timer_other_project.task.task_name
                
                return Response(
                    format_response(
                        success=False,
                        message=f"Cannot start timer. You already have an active timer for '{other_task_name}' in project '{other_project_name}'. Please stop that timer first.",
                        data={
                            'active_timer_info': {
                                'project_name': other_project_name,
                                'task_name': other_task_name,
                                'started_at': active_timer_other_project.start_time.isoformat(),
                            }
                        }
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # START new timer for this task
            new_timer = TaskTimer.objects.create(
                employee=current_user,
                task=task,
                work_date=today,
                start_time=timezone.now(),
                is_active=True
            )
            
            # Auto-update project status to "in_progress" when any task starts
            if project.status == 'not_started':
                project.status = 'in_progress'
                project.save()
            
            # Auto-update task status to "in_progress" when timer starts
            if task.status == 'not_started':
                task.status = 'in_progress'
                task.save()
            
            serializer = TaskTimerSerializer(new_timer)
            
            return Response(
                format_response(
                    success=True,
                    message=f"Timer started for task '{task.task_name}' in project '{project.project_name}'",
                    data={
                        'action': 'started',
                        'timer': serializer.data,
                        'project_info': {
                            'project_id': project.id,
                            'project_name': project.project_name,
                        }
                    }
                ),
                status=status.HTTP_200_OK
            )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error toggling timer: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get daily work time summary",
    operation_description="""
    Get employee's daily work time summary.
    
    Shows all work sessions for a specific date with total time worked.
    
    Query Parameters:
    - date: Date to get summary for (YYYY-MM-DD). Defaults to today.
    
    Returns:
    - List of all timer sessions for the date
    - Total time worked on the date
    - Breakdown by task
    
    Example:
    - /api/employee/timer/daily-summary/
    - /api/employee/timer/daily-summary/?date=2025-11-20
    """,
    manual_parameters=[
        openapi.Parameter(
            'date',
            openapi.IN_QUERY,
            description='Date to get summary for (YYYY-MM-DD). Defaults to today',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Daily summary retrieved successfully"
        ),
    },
    tags=['Employee - Task Timer']
)
def get_daily_timer_summary(request):
    """
    Get employee's daily work time summary.
    
    Endpoint: GET /api/employee/timer/daily-summary/
    
    Query Parameters:
    - date: Date in YYYY-MM-DD format (defaults to today)
    
    Returns all timer sessions and total time for the date.
    """
    try:
        from .models import TaskTimer
        from .serializers import TaskTimerSerializer
        from datetime import datetime
        from django.db.models import Sum
        
        current_user = request.user
        
        # Get date parameter or use today
        date_param = request.query_params.get('date', '').strip()
        if date_param:
            try:
                work_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            work_date = timezone.now().date()
        
        # Get all timers for this date
        timers = TaskTimer.objects.filter(
            employee=current_user,
            work_date=work_date
        ).select_related('task', 'task__project').order_by('start_time')
        
        # Calculate total time
        total_seconds = timers.aggregate(total=Sum('duration_seconds'))['total'] or 0
        
        # Add current active timer duration
        active_timer = timers.filter(is_active=True).first()
        if active_timer:
            current_duration = int((timezone.now() - active_timer.start_time).total_seconds())
            total_seconds += current_duration
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        total_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Group by task
        task_breakdown = {}
        for timer in timers:
            task_id = timer.task.id
            if task_id not in task_breakdown:
                task_breakdown[task_id] = {
                    'task_id': task_id,
                    'task_name': timer.task.task_name,
                    'project_name': timer.task.project.project_name,
                    'total_seconds': 0,
                    'sessions_count': 0
                }
            
            duration = timer.duration_seconds
            if timer.is_active:
                duration = int((timezone.now() - timer.start_time).total_seconds())
            
            task_breakdown[task_id]['total_seconds'] += duration
            task_breakdown[task_id]['sessions_count'] += 1
        
        # Format task breakdown
        for task_id, data in task_breakdown.items():
            secs = data['total_seconds']
            h = secs // 3600
            m = (secs % 3600) // 60
            s = secs % 60
            data['formatted'] = f"{h:02d}:{m:02d}:{s:02d}"
        
        # Serialize timers
        serializer = TaskTimerSerializer(timers, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Daily summary for {work_date}",
                data={
                    'date': work_date,
                    'employee': {
                        'id': current_user.id,
                        'username': current_user.username,
                        'full_name': current_user.get_full_name(),
                    },
                    'total_time': {
                        'seconds': total_seconds,
                        'formatted': total_formatted,
                        'hours': hours,
                        'minutes': minutes,
                    },
                    'active_timer': active_timer is not None,
                    'total_sessions': timers.count(),
                    'task_breakdown': list(task_breakdown.values()),
                    'sessions': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving daily summary: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== GET EMPLOYEE INFO API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get employee profile information",
    operation_description="""
    API endpoint to retrieve complete employee profile information.
    
    Returns:
    - Personal information (name, email, username)
    - Company information
    - Account details (role, status)
    - Profile image URL
    - Account creation and update dates
    - Total assigned tasks count
    - Total completed tasks count
    - Total work hours tracked today
    - Profile completeness percentage
    
    Only the authenticated employee can view their own profile information.
    """,
    responses={
        200: openapi.Response(
            description="Employee information retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Employee information retrieved successfully"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, example='john_doe'),
                            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john@example.com'),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John'),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe'),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING, example='John Doe'),
                            'company_name': openapi.Schema(type=openapi.TYPE_STRING, example='Acme Corporation'),
                            'country': openapi.Schema(type=openapi.TYPE_STRING, example='USA'),
                            'role': openapi.Schema(type=openapi.TYPE_STRING, example='Employee'),
                            'profile_image': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True, example='http://example.com/media/profile_images/user1.jpg'),
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                            'is_email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', example='2025-01-15T10:30:00Z'),
                            'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', example='2025-11-20T14:45:00Z'),
                            'stats': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_assigned_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                                    'completed_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=8),
                                    'in_progress_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                    'pending_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                    'total_work_hours_today': openapi.Schema(type=openapi.TYPE_STRING, example='6h 30m'),
                                    'total_work_seconds_today': openapi.Schema(type=openapi.TYPE_INTEGER, example=23400),
                                },
                            ),
                            'profile_completeness': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'percentage': openapi.Schema(type=openapi.TYPE_INTEGER, example=95),
                                    'missing_fields': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING),
                                        example=['profile_image']
                                    ),
                                }
                            ),
                        }
                    )
                }
            )
        ),
    },
    tags=['Employee - Profile']
)
def get_employee_info(request):
    """Get complete employee profile information"""
    try:
        user = request.user
        from .models import TaskTimer
        from datetime import date
        
        # Get task statistics
        assigned_tasks = Task.objects.filter(assigned_to=user)
        completed_tasks = assigned_tasks.filter(status='completed').count()
        in_progress_tasks = assigned_tasks.filter(status='in_progress').count()
        pending_tasks = assigned_tasks.filter(status='not_started').count()
        total_assigned = assigned_tasks.count()
        
        # Get today's work time
        today = date.today()
        today_timers = TaskTimer.objects.filter(employee=user, work_date=today)
        total_seconds = sum(t.duration_seconds for t in today_timers if t.duration_seconds)
        
        # Calculate hours and minutes
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        total_work_hours = f"{hours}h {minutes}m"
        
        # Profile completeness calculation
        required_fields = ['first_name', 'last_name', 'email', 'company_name']
        optional_fields = ['profile_image', 'country']
        
        completed_required = sum(1 for field in required_fields if getattr(user, field))
        completed_optional = sum(1 for field in optional_fields if getattr(user, field))
        
        total_possible = len(required_fields) + len(optional_fields)
        completeness = int((completed_required + completed_optional) / total_possible * 100) if total_possible > 0 else 0
        
        missing_fields = []
        for field in required_fields:
            if not getattr(user, field):
                missing_fields.append(field)
        
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}",
            'company_name': user.company_name,
            'country': user.country,
            'role': user.role,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'is_active': user.is_active,
            'is_email_verified': user.is_email_verified,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'stats': {
                'total_assigned_tasks': total_assigned,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'total_work_hours_today': total_work_hours,
                'total_work_seconds_today': total_seconds,
            },
            'profile_completeness': {
                'percentage': completeness,
                'missing_fields': missing_fields,
            }
        }
        
        return Response(
            format_response(
                success=True,
                message="Employee information retrieved successfully",
                data=response_data
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving employee information: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE TIMESHEET ENTRIES API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get employee timesheet entries",
    operation_description="""
    API endpoint for Employee to view their timesheet entries.
    
    Shows all time tracking sessions grouped by date with:
    - Date, Task name, Project name
    - Total hours worked
    - Task status and Project status
    - Actions available
    
    Query Parameters:
    - start_date: Filter from this date (YYYY-MM-DD)
    - end_date: Filter until this date (YYYY-MM-DD)
    - project_id: Filter by specific project
    - task_id: Filter by specific task
    - status: Filter by task status (not_started, in_progress, completed, blocked)
    
    Returns timesheet entries with weekly summary statistics.
    """,
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description='Start date for filtering (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description='End date for filtering (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'project_id',
            openapi.IN_QUERY,
            description='Filter by project ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'task_id',
            openapi.IN_QUERY,
            description='Filter by task ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by task status',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Timesheet entries retrieved successfully"
        ),
    },
    tags=['Employee - Timesheet']
)
def get_employee_timesheet_entries(request):
    """
    Get employee's timesheet entries with filters.
    
    Endpoint: GET /api/employee/timesheet/entries/
    
    Returns all time tracking sessions grouped by date.
    """
    try:
        from .models import TaskTimer
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count
        
        current_user = request.user
        
        # Get query parameters
        start_date_param = request.query_params.get('start_date', '').strip()
        end_date_param = request.query_params.get('end_date', '').strip()
        project_id = request.query_params.get('project_id', '').strip()
        task_id = request.query_params.get('task_id', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        
        # Default to last 7 days (including today) if no dates provided
        if not start_date_param:
            today = timezone.now().date()
            start_date = today - timedelta(days=6)  # 7 days ago (including today = 7 days)
        else:
            try:
                start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid start_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not end_date_param:
            end_date = timezone.now().date()  # Today
        else:
            try:
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid end_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Build query
        timers = TaskTimer.objects.filter(
            employee=current_user,
            work_date__range=[start_date, end_date]
        ).select_related('task', 'task__project').order_by('-work_date', '-start_time')
        
        # Apply filters
        if project_id:
            timers = timers.filter(task__project__id=project_id)
        
        if task_id:
            timers = timers.filter(task__id=task_id)
        
        if status_filter:
            timers = timers.filter(task__status=status_filter)
        
        # Build flat list of entries (not grouped by date)
        entries_list = []
        total_seconds = 0
        
        for timer in timers:
            # Calculate duration
            if timer.is_active:
                duration_seconds = int((timezone.now() - timer.start_time).total_seconds())
            else:
                duration_seconds = timer.duration_seconds
            
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            
            entries_list.append({
                'id': timer.id,
                'date': timer.work_date,
                'task': timer.task.task_name,
                'task_id': timer.task.id,
                'task_status': timer.task.status,
                'project': timer.task.project.project_name,
                'project_id': timer.task.project.id,
                'project_status': timer.task.project.status,
                'hours': f"{hours}h",
                'duration_seconds': duration_seconds,
                'duration_formatted': f"{hours:02d}:{minutes:02d}",
                'status': timer.task.status,
                'is_active': timer.is_active,
                'start_time': timer.start_time,
                'end_time': timer.end_time,
            })
            
            total_seconds += duration_seconds
        
        total_hours = total_seconds // 3600
        total_minutes = (total_seconds % 3600) // 60
        
        # Get unique counts
        unique_tasks = timers.values('task').distinct().count()
        unique_projects = timers.values('task__project').distinct().count()
        
        # Count by status
        status_counts = {
            'completed': timers.filter(task__status='completed').values('id').distinct().count(),
            'in_progress': timers.filter(task__status='in_progress').values('id').distinct().count(),
            'not_started': timers.filter(task__status='not_started').values('id').distinct().count(),
            'blocked': timers.filter(task__status='blocked').values('id').distinct().count(),
        }
        
        return Response(
            format_response(
                success=True,
                message="Timesheet entries retrieved successfully",
                data={
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date,
                    },
                    'weekly_summary': {
                        'total_working_hours': total_hours,
                        'total_working_minutes': total_minutes,
                        'total_formatted': f"{total_hours}h {total_minutes}m",
                        'newly_assigned': unique_tasks,
                        'submitted': status_counts['completed'],
                    },
                    'entries': entries_list,
                    'total_entries': timers.count(),
                    'status_breakdown': status_counts,
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving timesheet entries: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== SINGLE TIMER VIEW/EDIT API ======================
@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated, IsEmployee])
@swagger_auto_schema(
    operation_summary="Get or edit a single timer",
    operation_description="""
    Single view API for retrieving and updating a task timer.
    
    **GET**: Retrieve timer details
    **PATCH**: Update timer start/end times
    
    Allows employees to adjust:
    - start_time: When they started working on the task
    - end_time: When they stopped working on the task
    
    The timer will automatically recalculate the duration based on the new times.
    
    **GET Request:**
    GET /api/employee/timer/edit/{timer_id}/
    Returns all timer details with task information
    
    **PATCH Request:**
    PATCH /api/employee/timer/edit/{timer_id}/
    {
        "start_time": "2025-11-20T09:30:00Z",  // Optional - ISO 8601 format
        "end_time": "2025-11-20T17:30:00Z"     // Optional - ISO 8601 format
    }
    
    Rules:
    - At least one of start_time or end_time must be provided (for PATCH)
    - end_time must be after start_time
    - Employee can only edit their own timers
    - Cannot edit timer for a date after today
    
    Returns:
    - Timer details
    - Task information
    - Duration information (for PATCH: includes old and new values)
    - Total time for that day and task
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'start_time': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='date-time',
                description='New start time (ISO 8601 format, optional)'
            ),
            'end_time': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='date-time',
                description='New end time (ISO 8601 format, optional)'
            ),
        },
        example={
            'start_time': '2025-11-20T09:30:00Z',
        }
    ),
    responses={
        200: openapi.Response(
            description="Timer retrieved or updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'timer': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'old_values': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'new_values': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'total_time_today': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'seconds': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'formatted': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            ),
                        }
                    )
                }
            )
        ),
        400: openapi.Response(description="Invalid request data"),
        404: openapi.Response(description="Timer not found"),
    },
    tags=['Employee - Timer']
)
def edit_task_timer(request, timer_id):
    """
    Single view API for retrieving and updating a task timer.
    
    Endpoints:
    - GET /api/employee/timer/edit/{timer_id}/
    - PATCH /api/employee/timer/edit/{timer_id}/
    """
    try:
        from .models import TaskTimer
        from .serializers import TaskTimerSerializer
        from datetime import datetime
        
        current_user = request.user
        
        # Get the timer
        try:
            timer = TaskTimer.objects.get(id=timer_id, employee=current_user)
        except TaskTimer.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message=f"Timer with ID {timer_id} not found or not owned by you",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ========== GET REQUEST ==========
        if request.method == 'GET':
            serializer = TaskTimerSerializer(timer)
            
            # Format duration
            duration_seconds = timer.duration_seconds or 0
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Get total time for that day
            total_today = TaskTimer.objects.filter(
                employee=current_user,
                task=timer.task,
                work_date=timer.work_date
            ).aggregate(total=models.Sum('duration_seconds'))['total'] or 0
            
            total_hours = total_today // 3600
            total_minutes = (total_today % 3600) // 60
            total_seconds = total_today % 60
            total_formatted = f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"
            
            data = {
                'timer': serializer.data,
                'task_info': {
                    'task_id': timer.task.id,
                    'task_name': timer.task.task_name,
                    'project_id': timer.task.project.id,
                    'project_name': timer.task.project.project_name,
                },
                'duration': {
                    'seconds': duration_seconds,
                    'formatted': duration_formatted,
                },
                'total_time_today': {
                    'seconds': total_today,
                    'formatted': total_formatted,
                },
                'work_date': timer.work_date.isoformat(),
            }
            
            return Response(
                format_response(
                    success=True,
                    message=f"Timer retrieved successfully for task '{timer.task.task_name}'",
                    data=data
                ),
                status=status.HTTP_200_OK
            )
        
        # ========== PATCH REQUEST ==========
        elif request.method == 'PATCH':
            new_start_time_str = request.data.get('start_time')
            new_end_time_str = request.data.get('end_time')
            
            # Validate at least one time is provided
            if not new_start_time_str and not new_end_time_str:
                return Response(
                    format_response(
                        success=False,
                        message="At least one of start_time or end_time must be provided",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Store old values
            old_start = timer.start_time
            old_end = timer.end_time
            old_duration = timer.duration_seconds
            
            # Parse new times
            try:
                new_start_time = None
                new_end_time = None
                
                if new_start_time_str:
                    # Parse ISO 8601 format
                    if isinstance(new_start_time_str, str):
                        new_start_time = timezone.datetime.fromisoformat(
                            new_start_time_str.replace('Z', '+00:00')
                        )
                    else:
                        new_start_time = new_start_time_str
                
                if new_end_time_str:
                    # Parse ISO 8601 format
                    if isinstance(new_end_time_str, str):
                        new_end_time = timezone.datetime.fromisoformat(
                            new_end_time_str.replace('Z', '+00:00')
                        )
                    else:
                        new_end_time = new_end_time_str
            
            except (ValueError, TypeError) as e:
                return Response(
                    format_response(
                        success=False,
                        message=f"Invalid datetime format. Use ISO 8601 format (e.g., 2025-11-20T09:30:00Z): {str(e)}",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use existing times if not updating them
            final_start_time = new_start_time if new_start_time else timer.start_time
            final_end_time = new_end_time if new_end_time else timer.end_time
            
            # Validation: end_time must be after start_time
            if final_end_time and final_end_time <= final_start_time:
                return Response(
                    format_response(
                        success=False,
                        message="End time must be after start time",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validation: cannot edit timer for a future date
            today = timezone.now().date()
            if timer.work_date > today:
                return Response(
                    format_response(
                        success=False,
                        message="Cannot edit timers for future dates",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update timer
            timer.start_time = final_start_time
            if final_end_time:
                timer.end_time = final_end_time
            
            # Recalculate duration if both times exist
            if timer.start_time and timer.end_time:
                timer.duration_seconds = int((timer.end_time - timer.start_time).total_seconds())
            
            timer.save()
            
            # Get total time worked on this task for this date
            total_today = TaskTimer.objects.filter(
                employee=current_user,
                task=timer.task,
                work_date=timer.work_date
            ).aggregate(total=models.Sum('duration_seconds'))['total'] or 0
            
            hours = total_today // 3600
            minutes = (total_today % 3600) // 60
            seconds = total_today % 60
            total_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Prepare response
            serializer = TaskTimerSerializer(timer)
            
            old_formatted_duration = f"{old_duration // 3600:02d}:{(old_duration % 3600) // 60:02d}:{old_duration % 60:02d}"
            new_formatted_duration = f"{timer.duration_seconds // 3600:02d}:{(timer.duration_seconds % 3600) // 60:02d}:{timer.duration_seconds % 60:02d}"
            
            return Response(
                format_response(
                    success=True,
                    message=f"Timer updated successfully for task '{timer.task.task_name}'",
                    data={
                        'timer': serializer.data,
                        'old_values': {
                            'start_time': old_start.isoformat() if old_start else None,
                            'end_time': old_end.isoformat() if old_end else None,
                            'duration_seconds': old_duration,
                            'duration_formatted': old_formatted_duration,
                        },
                        'new_values': {
                            'start_time': timer.start_time.isoformat() if timer.start_time else None,
                            'end_time': timer.end_time.isoformat() if timer.end_time else None,
                            'duration_seconds': timer.duration_seconds,
                            'duration_formatted': new_formatted_duration,
                        },
                        'total_time_today': {
                            'seconds': total_today,
                            'formatted': total_formatted,
                            'task_name': timer.task.task_name,
                            'work_date': timer.work_date.isoformat(),
                        }
                    }
                ),
                status=status.HTTP_200_OK
            )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error processing request: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

