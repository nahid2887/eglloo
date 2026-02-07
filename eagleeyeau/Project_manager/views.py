from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from eagleeyeau.response_formatter import format_response
from authentication.models import User
from timesheet.models import TimeEntry
from estimator.models import Estimate
from .models import Project, Task
from .serializers import (
    EmployeeSerializer, TimeEntrySerializer, EmployeeTimesheetDetailSerializer,
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateSerializer,
    TaskSerializer
)


# ====================== PERMISSIONS ======================
class IsProjectManager(permissions.BasePermission):
    """Allow only Project Manager or Admin"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['Project Manager', 'Admin']
        )


# ====================== EMPLOYEE LIST API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="Get company employees with search",
    operation_description="""
    API endpoint for Project Manager to view all Employee role users from the same company.
    
    Query Parameters:
    - q: Optional search parameter. Searches by first_name, last_name, email, or username (case-insensitive, partial match)
    
    Returns:
    - List of all Employee users from the same company as the logged-in user
    - Only accessible by Project Manager or Admin users
    """,
    manual_parameters=[
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description='Search by employee name (first_name, last_name, email, or username)',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    tags=['Project Manager - Employees']
)
def get_company_employees(request):
    """
    API endpoint for Project Manager to view all Employee role users from the same company.
    
    Endpoint: GET /api/project-manager/employees/
    
    Query Parameters:
    - q: Search by employee name (first_name or last_name, case-insensitive)
    
    Returns:
    - List of all Employee users from the same company as the logged-in user
    - Only accessible by Project Manager or Admin users
    
    Examples:
    - /api/project-manager/employees/
    - /api/project-manager/employees/?q=john
    - /api/project-manager/employees/?q=smith
    """
    try:
        # Get the current user's company
        current_user = request.user
        company_name = current_user.company_name
        
        if not company_name:
            return Response(
                format_response(
                    success=False,
                    message="Your user account doesn't have a company assigned",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all Employee users from the same company
        employees = User.objects.filter(
            company_name=company_name,
            role='Employee'
        )
        
        # Apply search filter if provided
        search_query = request.query_params.get('q', '').strip()
        filters_applied = {'q': search_query if search_query else None}
        
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        employees = employees.order_by('first_name', 'last_name')
        employee_count = employees.count()
        
        # Serialize the data
        serializer = EmployeeSerializer(employees, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {employee_count} employees from {company_name}",
                data={
                    'company': company_name,
                    'total_employees': employee_count,
                    'filters_applied': filters_applied,
                    'employees': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving employees: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
def get_company_employees_filtered(request):
    """
    API endpoint with filtering options for Project Manager.
    
    Endpoint: GET /api/project-manager/employees/search/
    
    Query Parameters:
    - search: Search by first_name, last_name, or email
    - is_verified: Filter by email verification status (true/false)
    
    Example: /api/project-manager/employees/search/?search=john&is_verified=true
    """
    try:
        current_user = request.user
        company_name = current_user.company_name
        
        if not company_name:
            return Response(
                format_response(
                    success=False,
                    message="Your user account doesn't have a company assigned",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start with base query
        employees = User.objects.filter(
            company_name=company_name,
            role='Employee'
        )
        
        # Apply search filter
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )
        
        # Apply email verification filter
        is_verified = request.query_params.get('is_verified', '').strip()
        if is_verified.lower() in ['true', '1']:
            employees = employees.filter(is_email_verified=True)
        elif is_verified.lower() in ['false', '0']:
            employees = employees.filter(is_email_verified=False)
        
        employees = employees.order_by('first_name', 'last_name')
        employee_count = employees.count()
        
        serializer = EmployeeSerializer(employees, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {employee_count} employees matching criteria",
                data={
                    'company': company_name,
                    'total_employees': employee_count,
                    'filters_applied': {
                        'search': search_query if search_query else None,
                        'is_verified': is_verified if is_verified else None,
                    },
                    'employees': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving employees: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== TIMESHEET API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
def get_company_timesheets(request):
    """
    API endpoint to view all timesheets from employees of the same company.
    
    Endpoint: GET /api/project-manager/timesheets/
    
    Query Parameters:
    - employee_name: Filter by employee first_name or last_name (optional)
    - start_date: Start date for timesheet (YYYY-MM-DD format, optional)
    - end_date: End date for timesheet (YYYY-MM-DD format, optional)
    - attendance: Filter by attendance status (Present/Absent/Half Day, optional)
    
    Examples:
    - /api/project-manager/timesheets/
    - /api/project-manager/timesheets/?employee_name=Jane
    - /api/project-manager/timesheets/?start_date=2025-02-01&end_date=2025-02-28
    - /api/project-manager/timesheets/?employee_name=Jane&start_date=2025-02-01
    """
    try:
        current_user = request.user
        company_name = current_user.company_name
        
        if not company_name:
            return Response(
                format_response(
                    success=False,
                    message="Your user account doesn't have a company assigned",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all employees from the company
        company_employees = User.objects.filter(
            company_name=company_name,
            role='Employee'
        )
        
        # Start with timesheet entries from company employees
        timesheets = TimeEntry.objects.filter(
            user__in=company_employees
        )
        
        # Apply employee name filter
        employee_name = request.query_params.get('employee_name', '').strip()
        if employee_name:
            timesheets = timesheets.filter(
                Q(user__first_name__icontains=employee_name) |
                Q(user__last_name__icontains=employee_name)
            )
        
        # Apply date range filter
        start_date = request.query_params.get('start_date', '').strip()
        end_date = request.query_params.get('end_date', '').strip()
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                timesheets = timesheets.filter(date__gte=start_date_obj)
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid start_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                timesheets = timesheets.filter(date__lte=end_date_obj)
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid end_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply attendance filter
        attendance = request.query_params.get('attendance', '').strip()
        if attendance in ['Present', 'Absent', 'Half Day']:
            timesheets = timesheets.filter(attendance=attendance)
        
        # Order by date descending, then by entry_time
        timesheets = timesheets.order_by('-date', '-entry_time')
        
        total_entries = timesheets.count()
        
        # Serialize the data
        serializer = TimeEntrySerializer(timesheets, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {total_entries} timesheet entries",
                data={
                    'company': company_name,
                    'total_entries': total_entries,
                    'filters_applied': {
                        'employee_name': employee_name if employee_name else None,
                        'start_date': start_date if start_date else None,
                        'end_date': end_date if end_date else None,
                        'attendance': attendance if attendance else None,
                    },
                    'timesheets': serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving timesheets: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
def get_employee_timesheet_detail(request, employee_id):
    """
    API endpoint to view detailed timesheet for a specific employee.
    
    Endpoint: GET /api/project-manager/timesheets/employee/<employee_id>/
    
    Query Parameters:
    - start_date: Start date for timesheet (YYYY-MM-DD format, optional, defaults to 7 days ago)
    - end_date: End date for timesheet (YYYY-MM-DD format, optional, defaults to today)
    
    Returns: Complete employee information with all timesheet entries for the period
    """
    try:
        current_user = request.user
        company_name = current_user.company_name
        
        if not company_name:
            return Response(
                format_response(
                    success=False,
                    message="Your user account doesn't have a company assigned",
                    data=None
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the employee - must be from the same company
        try:
            employee = User.objects.get(
                id=employee_id,
                company_name=company_name,
                role='Employee'
            )
        except User.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message="Employee not found or not in your company",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get date range
        today = timezone.now().date()
        start_date = request.query_params.get('start_date', '').strip()
        end_date = request.query_params.get('end_date', '').strip()
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid start_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Default to last 7 days
            start_date_obj = today - timedelta(days=7)
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    format_response(
                        success=False,
                        message="Invalid end_date format. Use YYYY-MM-DD",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            end_date_obj = today
        
        # Get timesheet entries for the period
        timesheet_entries = TimeEntry.objects.filter(
            user=employee,
            date__range=[start_date_obj, end_date_obj]
        ).order_by('-date', '-entry_time')
        
        # Serialize employee data
        employee_serializer = EmployeeSerializer(employee)
        timesheet_serializer = TimeEntrySerializer(timesheet_entries, many=True)
        
        # Calculate total hours
        total_seconds = 0
        for entry in timesheet_entries:
            if entry.total_working_time:
                total_seconds += int(entry.total_working_time.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        total_hours = f"{hours}h {minutes}m"
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved timesheet for {employee.get_full_name()}",
                data={
                    'employee': employee_serializer.data,
                    'period': {
                        'start_date': start_date_obj.isoformat(),
                        'end_date': end_date_obj.isoformat(),
                    },
                    'summary': {
                        'total_entries': timesheet_entries.count(),
                        'total_hours': total_hours,
                        'attendance_breakdown': {
                            'present': timesheet_entries.filter(attendance='Present').count(),
                            'absent': timesheet_entries.filter(attendance='Absent').count(),
                            'half_day': timesheet_entries.filter(attendance='Half Day').count(),
                        }
                    },
                    'timesheet_entries': timesheet_serializer.data
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving employee timesheet: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== ESTIMATE LIST API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="Get all estimates with search and filter",
    operation_description="""
    API endpoint for Project Manager to view all estimates.
    
    Query Parameters:
    - q: Optional search parameter. Searches by serial_number, estimate_number, client_name, or project_name (case-insensitive, partial match)
    - status: Optional filter by estimate status (pending, sent, approved, rejected)
    
    Returns:
    - List of all estimates with summary information
    - Only accessible by Project Manager or Admin users
    """,
    manual_parameters=[
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description='Search by serial number, estimate number, client name, or project name',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by estimate status: pending, sent, approved, rejected',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="Estimates retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'status_summary': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'sent': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'approved': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'rejected': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        }
                    )
                }
            )
        ),
    },
    tags=['Project Manager - Estimates']
)
def get_estimates_list(request):
    """
    Project Manager can view all estimates with search and filter by status.
    
    Endpoint: GET /api/project-manager/estimates/
    
    Query Parameters:
    - q: Search by serial number, estimate number, client name, or project name
    - status: Filter by status (pending, sent, approved, rejected)
    
    Examples:
    - /api/project-manager/estimates/ - Get all estimates
    - /api/project-manager/estimates/?status=approved - Get only approved estimates
    - /api/project-manager/estimates/?status=pending - Get only pending estimates
    - /api/project-manager/estimates/?q=ABC - Search for "ABC" in all fields
    - /api/project-manager/estimates/?status=approved&q=ABC - Combined filter
    """
    try:
        from estimator.models import Estimate
        from estimator.serializers import EstimateListSerializer
        
        # Get all estimates
        estimates = Estimate.objects.all()
        
        # Search by query parameter
        search_query = request.query_params.get('q', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        
        filters_applied = {
            'q': search_query if search_query else None,
            'status': status_filter if status_filter else None,
        }
        
        if search_query:
            estimates = estimates.filter(
                Q(serial_number__icontains=search_query) |
                Q(estimate_number__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(project_name__icontains=search_query)
            )
        
        # Filter by status
        valid_statuses = ['pending', 'sent', 'approved', 'rejected']
        if status_filter and status_filter in valid_statuses:
            estimates = estimates.filter(status=status_filter)
        
        # Order by created_at descending
        estimates = estimates.order_by('-created_at')
        
        # Calculate status summary of ALL estimates (not just filtered)
        all_estimates = Estimate.objects.all()
        status_summary = {
            'pending': all_estimates.filter(status='pending').count(),
            'sent': all_estimates.filter(status='sent').count(),
            'approved': all_estimates.filter(status='approved').count(),
            'rejected': all_estimates.filter(status='rejected').count(),
        }
        
        # Serialize data
        serializer = EstimateListSerializer(estimates, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {estimates.count()} estimates",
                data={
                    'total_count': estimates.count(),
                    'filters_applied': filters_applied,
                    'status_summary': status_summary,
                    'results': serializer.data,
                }
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving estimates: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== ESTIMATE DETAIL API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="Get estimate details",
    operation_description="""
    API endpoint for Project Manager to view detailed information about a specific estimate.
    
    URL Parameters:
    - estimate_id: The ID of the estimate to retrieve
    
    Returns:
    - Complete estimate details including all items, costs, and calculations
    - Only accessible by Project Manager or Admin users
    """,
    tags=['Project Manager - Estimates']
)
def get_estimate_detail(request, estimate_id):
    """Project Manager can view estimate details"""
    try:
        from estimator.models import Estimate
        from estimator.serializers import EstimateSerializer
        
        # Get the specific estimate
        estimate = Estimate.objects.get(id=estimate_id)
        
        # Serialize data
        serializer = EstimateSerializer(estimate)
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved estimate {estimate.serial_number}",
                data=serializer.data
            ),
            status=status.HTTP_200_OK
        )
    
    except Estimate.DoesNotExist:
        return Response(
            format_response(
                success=False,
                message=f"Estimate with ID {estimate_id} not found",
                data=None
            ),
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving estimate: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== PROJECT VIEWSET ======================
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project management.
    Project Manager can create projects from approved estimates and manage them.
    """
    # Default: authenticated required. We'll allow authenticated users to CREATE projects
    # (estimators can quickly create a project from an estimate). Other actions remain
    # restricted to Project Manager / Admin via get_permissions().
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """Per-action permissions: allow any authenticated user to create,
        restrict other actions to Project Manager/Admin."""
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsProjectManager()]
    
    def get_queryset(self):
        """Project Managers see all projects, Employees see only assigned projects"""
        user = self.request.user
        is_project_manager = user.role in ['Project Manager', 'Admin']
        
        if is_project_manager:
            return Project.objects.all().order_by('-creating_date')
        else:
            return Project.objects.filter(assigned_to=user).order_by('-creating_date')
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        return ProjectDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="List all projects",
        operation_description="Get all projects with task counts and creator info. Project Manager only.",
        responses={200: ProjectListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description='Filter by project status',
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Projects']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            format_response(
                success=True,
                message=f"Projects retrieved successfully (Total: {queryset.count()})",
                data={'total_count': queryset.count(), 'results': serializer.data}
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Create project from approved estimate",
        operation_description="""
        Create a new project from an approved estimate.
        
        Requirements:
        - The estimate status MUST be 'approved'
        - Only one project can be created per estimate
        
        Data Populated from Estimate:
        - total_amount (from estimate total_with_tax)
        - estimated_cost (from estimate total_cost)
        - rooms (from estimate targeted_rooms)
        
        Response includes:
        - tasks_count: Total number of tasks in the project (0 initially)
        - assigned_employees_count: Number of unique employees assigned to tasks
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['estimate', 'project_name', 'client_name'],
            properties={
                'estimate': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the approved estimate'),
                'project_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                'client_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the client'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Project description (optional)'),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Project start date (optional)'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Project end date (optional)'),
                'assigned_to': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to assign project to (optional)'),
            },
            example={
                'estimate': 1,
                'project_name': 'Office Renovation',
                'client_name': 'Acme Corporation',
                'description': 'Complete office renovation project',
                'start_date': '2025-12-01',
                'end_date': '2026-03-31',
                'assigned_to': 5
            }
        ),
        responses={201: ProjectDetailSerializer},
        tags=['Projects']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                format_response(success=False, message="Validation error", data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate estimate exists and that no project already exists for it.
        try:
            estimate = serializer.validated_data.get('estimate')
            if not estimate:
                return Response(
                    format_response(success=False, message="Estimate is required", data=None),
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Allow fast creation from an estimate regardless of approval status.
            if Project.objects.filter(estimate=estimate).exists():
                return Response(
                    format_response(
                        success=False,
                        message="Project already exists for this estimate",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Estimate.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        
        project = serializer.save(created_by=request.user)
        response_serializer = ProjectDetailSerializer(project)
        
        return Response(
            format_response(
                success=True,
                message="Project created from estimate successfully",
                data=response_serializer.data
            ),
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Retrieve project details",
        operation_description="Get full project details with all tasks",
        responses={200: ProjectDetailSerializer},
        tags=['Projects']
    )
    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project)
        return Response(
            format_response(
                success=True,
                message="Project retrieved successfully",
                data=serializer.data
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Update project",
        operation_description="Update project details (status, dates, assigned_to, etc.)",
        request_body=ProjectDetailSerializer,
        responses={200: ProjectDetailSerializer},
        tags=['Projects']
    )
    def partial_update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                format_response(success=False, message="Validation error", data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = serializer.save()
        return Response(
            format_response(
                success=True,
                message="Project updated successfully",
                data=ProjectDetailSerializer(project).data
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Get project Gantt chart data (grid view)",
        operation_description="""
        Get project data formatted for Gantt/grid chart visualization.
        
        Returns:
        - Project details (name, client, status, dates)
        - All tasks with their timeline (start_date to due_date)
        - Each task shows task_name, room, priority, status, assigned employee
        
        Query Parameters (Optional):
        - room: Filter tasks by room name (e.g., ?room=Kitchen)
        - start_date: Filter tasks starting from this date (e.g., ?start_date=2025-12-01)
        - end_date: Filter tasks ending before this date (e.g., ?end_date=2025-12-31)
        
        Filter Examples:
        - /api/project-manager/projects/1/gantt-chart/?room=Kitchen
        - /api/project-manager/projects/1/gantt-chart/?start_date=2025-12-01&end_date=2025-12-31
        - /api/project-manager/projects/1/gantt-chart/?room=Kitchen&start_date=2025-12-01
        
        This endpoint is designed for calendar/Gantt chart UI components.
        """,
        manual_parameters=[
            openapi.Parameter(
                'room',
                openapi.IN_QUERY,
                description='Filter tasks by room name',
                type=openapi.TYPE_STRING,
                required=False
            ),
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
        ],
        responses={200: openapi.Response(
            description="Gantt chart data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'project_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'client_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'project_start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'project_end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'filtered_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'tasks': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'task_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'room': openapi.Schema(type=openapi.TYPE_STRING),
                                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                'status': openapi.Schema(type=openapi.TYPE_STRING),
                                'priority': openapi.Schema(type=openapi.TYPE_STRING),
                                'phase': openapi.Schema(type=openapi.TYPE_STRING),
                                'assigned_employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    )
                },
                example={
                    'project_id': 1,
                    'project_name': 'Office Renovation',
                    'client_name': 'Acme Corporation',
                    'status': 'in_progress',
                    'project_start_date': '2025-12-01',
                    'project_end_date': '2026-03-31',
                    'total_tasks': 5,
                    'filtered_tasks': 2,
                    'tasks': [
                        {
                            'id': 1,
                            'task_name': 'Kitchen Design',
                            'room': 'Kitchen',
                            'start_date': '2025-12-01',
                            'due_date': '2025-12-15',
                            'status': 'in_progress',
                            'priority': 'high',
                            'phase': 'design',
                            'assigned_employee_name': 'john_smith'
                        },
                        {
                            'id': 2,
                            'task_name': 'Plumbing Work',
                            'room': 'Bathroom',
                            'start_date': '2025-12-10',
                            'due_date': '2025-12-25',
                            'status': 'not_started',
                            'priority': 'high',
                            'phase': 'construction',
                            'assigned_employee_name': 'jane_doe'
                        }
                    ]
                }
            )
        )},
        tags=['Projects']
    )
    def gantt_chart(self, request, pk=None):
        """Get project in Gantt chart format for grid/timeline visualization with optional filters"""
        project = self.get_object()
        tasks = project.tasks.all().order_by('priority', 'due_date')
        
        # Get filter parameters from query string
        room_filter = request.query_params.get('room', '').strip()
        start_date_filter = request.query_params.get('start_date', '').strip()
        end_date_filter = request.query_params.get('end_date', '').strip()
        
        # Apply room filter - exact match (case-insensitive)
        if room_filter:
            tasks = tasks.filter(room__iexact=room_filter)
        
        # Apply start_date filter
        if start_date_filter:
            try:
                from datetime import datetime
                start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
                tasks = tasks.filter(start_date__gte=start_date)
            except (ValueError, AttributeError):
                pass  # Invalid date format, ignore filter
        
        # Apply end_date filter
        if end_date_filter:
            try:
                from datetime import datetime
                end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()
                tasks = tasks.filter(due_date__lte=end_date)
            except (ValueError, AttributeError):
                pass  # Invalid date format, ignore filter
        
        
        from .serializers import TaskGanttSerializer
        
        # Count tasks after filters are applied
        filtered_tasks_count = tasks.count()
        
        data = {
            'project_id': project.id,
            'project_name': project.project_name,
            'client_name': project.client_name,
            'status': project.status,
            'project_start_date': project.start_date,
            'project_end_date': project.end_date,
            'total_tasks': project.tasks.count(),
            'filtered_tasks': filtered_tasks_count,
            'tasks': TaskGanttSerializer(tasks, many=True).data
        }
        
        return Response(
            format_response(
                success=True,
                message=f"Gantt chart data for project '{project.project_name}'",
                data=data
            ),
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Upload a document to project",
        operation_description="Upload a file/document associated with a project (PDF, image, doc, etc.)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['file', 'document_name'],
            properties={
                'file': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='The file to upload'),
                'document_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name/title of the document'),
                'document_type': openapi.Schema(type=openapi.TYPE_STRING, description='File type (pdf, image, doc, etc.) - optional'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Optional description of the document'),
            }
        ),
        responses={201: openapi.Response(description="Document uploaded successfully")},
        tags=['Projects - Documents']
    )
    def upload_document(self, request, pk=None):
        """Upload a document to a project"""
        try:
            project = self.get_object()
            
            # Check for required fields
            if 'file' not in request.FILES:
                return Response(
                    format_response(
                        success=False,
                        message="File is required",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            document_name = request.data.get('document_name', '').strip()
            if not document_name:
                return Response(
                    format_response(
                        success=False,
                        message="Document name is required",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the ProjectDocument
            from .models import ProjectDocument
            document = ProjectDocument.objects.create(
                project=project,
                file=request.FILES['file'],
                document_name=document_name,
                document_type=request.data.get('document_type', 'file').strip(),
                description=request.data.get('description', '').strip() or None,
                uploaded_by=request.user
            )
            
            from .serializers import ProjectDocumentSerializer
            serializer = ProjectDocumentSerializer(document)
            
            return Response(
                format_response(
                    success=True,
                    message="Document uploaded successfully",
                    data=serializer.data
                ),
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                format_response(
                    success=False,
                    message=f"Error uploading document: {str(e)}",
                    data=None
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Download project as PDF",
        operation_description="Download complete project information as a single PDF file with all details, tasks, and metadata.",
        responses={200: openapi.Response(description="PDF file with all project information")},
        tags=['Projects - Documents']
    )
    def download_documents(self, request, pk=None):
        """Download complete project information as PDF"""
        try:
            project = self.get_object()
            
            # Generate PDF with all project info
            pdf_content = self._generate_project_pdf(project)
            
            if not pdf_content:
                return Response(
                    format_response(
                        success=False,
                        message="Error generating PDF",
                        data=None
                    ),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            from django.http import FileResponse
            import io
            
            pdf_buffer = io.BytesIO(pdf_content)
            filename = f"{project.project_name}_Project_Report.pdf"
            response = FileResponse(
                pdf_buffer,
                content_type='application/pdf',
                as_attachment=True,
                filename=filename
            )
            return response
        
        except Exception as e:
            return Response(
                format_response(
                    success=False,
                    message=f"Error downloading project: {str(e)}",
                    data=None
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_project_pdf(self, project):
        """Generate a comprehensive PDF of the project with all information"""
        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from datetime import datetime
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=colors.HexColor('#2d5aa6'),
                spaceAfter=8,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            )
            
            # Title
            elements.append(Paragraph(f"Project Report: {project.project_name}", title_style))
            elements.append(Spacer(1, 0.15 * inch))
            
            # ===== PROJECT DETAILS =====
            elements.append(Paragraph("PROJECT DETAILS", heading_style))
            project_data = [
                ['Field', 'Value'],
                ['Project Name', project.project_name or 'N/A'],
                ['Client Name', project.client_name or 'N/A'],
                ['Status', project.status.replace('_', ' ').title()],
                ['Created Date', project.creating_date.strftime('%Y-%m-%d') if project.creating_date else 'N/A'],
                ['Start Date', project.start_date.strftime('%Y-%m-%d') if project.start_date else 'N/A'],
                ['End Date', project.end_date.strftime('%Y-%m-%d') if project.end_date else 'N/A'],
                ['Total Amount', f"${project.total_amount:,.2f}"],
                ['Estimated Cost', f"${project.estimated_cost:,.2f}"],
                ['Created By', f"{project.created_by.first_name} {project.created_by.last_name}" if project.created_by else 'N/A'],
                ['Assigned To', f"{project.assigned_to.first_name} {project.assigned_to.last_name}" if project.assigned_to else 'Unassigned'],
            ]
            
            project_table = Table(project_data, colWidths=[1.8*inch, 3.7*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(project_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # ===== DESCRIPTION =====
            if project.description:
                elements.append(Paragraph("DESCRIPTION", heading_style))
                elements.append(Paragraph(project.description, styles['BodyText']))
                elements.append(Spacer(1, 0.15 * inch))
            
            # ===== ROOMS =====
            if project.rooms:
                elements.append(Paragraph("ROOMS INVOLVED", heading_style))
                rooms_text = ', '.join(project.rooms) if isinstance(project.rooms, list) else str(project.rooms)
                elements.append(Paragraph(rooms_text, styles['BodyText']))
                elements.append(Spacer(1, 0.15 * inch))
            
            # ===== TASKS SUMMARY =====
            elements.append(Paragraph("TASKS SUMMARY", heading_style))
            tasks = project.tasks.all()
            task_count = tasks.count()
            completed_count = tasks.filter(status='completed').count()
            in_progress_count = tasks.filter(status='in_progress').count()
            not_started_count = tasks.filter(status='not_started').count()
            blocked_count = tasks.filter(status='blocked').count()
            
            task_summary_data = [
                ['Status', 'Count'],
                ['Total Tasks', str(task_count)],
                ['Completed', str(completed_count)],
                ['In Progress', str(in_progress_count)],
                ['Not Started', str(not_started_count)],
                ['Blocked', str(blocked_count)],
            ]
            
            task_table = Table(task_summary_data, colWidths=[2.5*inch, 2*inch])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(task_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # ===== DETAILED TASKS LIST =====
            if task_count > 0:
                elements.append(Paragraph("DETAILED TASKS", heading_style))
                
                tasks_list_data = [
                    ['Task', 'Room', 'Status', 'Priority', 'Assigned To', 'Due Date']
                ]
                
                for task in tasks.order_by('priority', 'due_date'):
                    assigned_to = task.assigned_employee.username if task.assigned_employee else 'Unassigned'
                    due_date = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'N/A'
                    
                    tasks_list_data.append([
                        task.task_name[:30],
                        task.room or 'N/A',
                        task.status.replace('_', ' ').title(),
                        task.priority.title(),
                        assigned_to,
                        due_date
                    ])
                
                tasks_list_table = Table(tasks_list_data, colWidths=[1.4*inch, 1*inch, 1.1*inch, 0.9*inch, 1.1*inch, 1*inch])
                tasks_list_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tasks_list_table)
                elements.append(Spacer(1, 0.15 * inch))
            
            # ===== DOCUMENTS =====
            from .models import ProjectDocument
            documents = ProjectDocument.objects.filter(project=project)
            if documents.exists():
                elements.append(Paragraph("DOCUMENTS", heading_style))
                
                docs_data = [
                    ['Document Name', 'Type', 'Uploaded By', 'Date']
                ]
                
                for doc in documents.order_by('-uploaded_at'):
                    uploader = doc.uploaded_by.username if doc.uploaded_by else 'System'
                    date = doc.uploaded_at.strftime('%Y-%m-%d %H:%M') if doc.uploaded_at else 'N/A'
                    
                    docs_data.append([
                        doc.document_name[:35],
                        doc.document_type,
                        uploader,
                        date
                    ])
                
                docs_table = Table(docs_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
                docs_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                ]))
                elements.append(docs_table)
                elements.append(Spacer(1, 0.15 * inch))
            
            # ===== FOOTER =====
            elements.append(Spacer(1, 0.3 * inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1
            )
            elements.append(Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Lignaflow Project Management System",
                footer_style
            ))
            
            # Build PDF
            doc.build(elements)
            return buffer.getvalue()
        
        except ImportError:
            return None
        except Exception as e:
            return None


# ====================== TASK VIEWSET ======================
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task management within projects.
    Project Manager can create and manage tasks.
    """
    # Allow authenticated users to interact; enforce per-action ownership/role checks below
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        """Get tasks filtered by project"""
        project_id = self.kwargs.get('project_id')
        if project_id:
            return Task.objects.filter(project_id=project_id).order_by('priority', 'due_date')
        return Task.objects.all().order_by('priority', 'due_date')
    
    @swagger_auto_schema(
        operation_summary="List tasks for a project",
        operation_description="Get all tasks for a specific project",
        responses={200: TaskSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description='Filter by task status',
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Tasks']
    )
    def list(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                format_response(success=False, message="Project not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = self.get_queryset()
        status_filter = request.query_params.get('status', '').strip()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            format_response(
                success=True,
                message=f"Tasks retrieved for project {project.project_name}",
                data={'total_count': queryset.count(), 'results': serializer.data}
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Create task in project",
        operation_description="""
        Create a new task and assign it to an employee within a project.
        
        Task Assignment:
        - Use 'assigned_employee' field with the User ID to assign a task to an employee
        - Leave 'assigned_employee' as null if you want to create unassigned tasks first
        
        Priority Levels:
        - 'low': Low priority tasks
        - 'medium': Medium priority tasks (default)
        - 'high': High priority tasks
        
        Task Status Options:
        - 'not_started': Task hasn't started yet
        - 'in_progress': Task is currently being worked on
        - 'completed': Task is finished
        - 'blocked': Task is blocked/delayed
        
        Task Phase Options:
        - 'planning': Planning phase
        - 'design': Design phase
        - 'procurement': Procurement phase
        - 'construction': Construction phase
        - 'handover': Handover phase
        
        Response includes:
        - assigned_employee_name: Full name of assigned employee (if assigned)
        - created_by_name: Full name of who created the task
        - All task details with dates and status
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['task_name', 'priority', 'due_date'],
            properties={
                'task_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the task'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed task description (optional)'),
                'room': openapi.Schema(type=openapi.TYPE_STRING, description='Target room for this task (optional, e.g., "Kitchen", "Living Room")'),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, enum=['low', 'medium', 'high'], description='Task priority level'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['not_started', 'in_progress', 'completed', 'blocked'], description='Task status (default: not_started)'),
                'phase': openapi.Schema(type=openapi.TYPE_STRING, enum=['planning', 'design', 'procurement', 'construction', 'handover'], description='Project phase for this task (optional)'),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Task start date (optional)'),
                'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Task due date'),
                'assigned_employee': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID of employee to assign task to (optional, can be assigned later)'),
            },
            example={
                'task_name': 'Kitchen Design',
                'description': 'Design and plan kitchen layout and materials',
                'room': 'Kitchen',
                'priority': 'high',
                'phase': 'design',
                'status': 'not_started',
                'start_date': '2025-12-01',
                'due_date': '2025-12-15',
                'assigned_employee': 7
            }
        ),
        responses={201: TaskSerializer},
        tags=['Tasks']
    )
    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                format_response(success=False, message="Project not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        # Permission: allow if request.user is project creator or a Project Manager/Admin
        is_project_manager = request.user.role in ['Project Manager', 'Admin'] if hasattr(request.user, 'role') else request.user.is_staff
        is_project_creator = project.created_by == request.user
        if not (is_project_manager or is_project_creator):
            return Response(
                format_response(success=False, message="Permission denied: only project creator or Project Manager can add tasks", data=None),
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                format_response(success=False, message="Validation error", data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = serializer.save(project=project, created_by=request.user)
        return Response(
            format_response(
                success=True,
                message="Task created successfully",
                data=TaskSerializer(task).data
            ),
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Retrieve task details",
        operation_description="Get task details",
        responses={200: TaskSerializer},
        tags=['Tasks']
    )
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task)
        return Response(
            format_response(
                success=True,
                message="Task retrieved successfully",
                data=serializer.data
            ),
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Update task",
        operation_description="Update task details",
        request_body=TaskSerializer,
        responses={200: TaskSerializer},
        tags=['Tasks']
    )
    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        # Permission: only project creator or Project Manager/Admin or task creator can update
        project = task.project
        is_project_manager = request.user.role in ['Project Manager', 'Admin'] if hasattr(request.user, 'role') else request.user.is_staff
        is_project_creator = project.created_by == request.user
        is_task_creator = task.created_by == request.user
        if not (is_project_manager or is_project_creator or is_task_creator):
            return Response(
                format_response(success=False, message="Permission denied: cannot update this task", data=None),
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(task, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                format_response(success=False, message="Validation error", data=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = serializer.save()
        return Response(
            format_response(
                success=True,
                message="Task updated successfully",
                data=TaskSerializer(task).data
            ),
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Delete task",
        operation_description="""
        Delete a task from the project.
        
        Permission:
        - Project creator can delete any task in their project
        - Task creator can delete their own task
        - Project Manager/Admin can delete any task
        - Others cannot delete
        
        Response: 204 No Content (task successfully deleted)
        """,
        responses={
            204: openapi.Response(description="Task deleted successfully"),
            403: openapi.Response(description="Permission denied - cannot delete this task"),
            404: openapi.Response(description="Task or project not found"),
        },
        tags=['Tasks']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a task: only project creator, task creator or Project Manager/Admin can delete."""
        task = self.get_object()
        project = task.project
        is_project_manager = request.user.role in ['Project Manager', 'Admin'] if hasattr(request.user, 'role') else request.user.is_staff
        is_project_creator = project.created_by == request.user
        is_task_creator = task.created_by == request.user
        if not (is_project_manager or is_project_creator or is_task_creator):
            return Response(
                format_response(success=False, message="Permission denied: cannot delete this task", data=None),
                status=status.HTTP_403_FORBIDDEN
            )

        task_id = task.id
        task.delete()
        return Response(
            format_response(success=True, message=f"Task {task_id} deleted successfully", data={'deleted_id': task_id}),
            status=status.HTTP_204_NO_CONTENT
        )


# ====================== PROJECT MANAGER ALL PROJECTS VIEW ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="Get all projects for Project Manager",
    operation_description="""
    API endpoint for Project Manager to view all projects with progress tracking.
    
    This endpoint returns:
    - All projects managed by the Project Manager
    - Progress percentage (based on completed tasks vs total tasks)
    - Total project tasks count
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
        "message": "Retrieved 5 projects",
        "data": {
            "statistics": {
                "total_projects": 5,
                "completed_projects": 2,
                "due_projects": 2,
                "cancelled_projects": 1
            },
            "projects": [...]
        }
    }
    """,
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description='Filter by project status',
            type=openapi.TYPE_STRING,
            enum=['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description='Search in project name or client name',
            type=openapi.TYPE_STRING
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
                            'projects': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        }
                    )
                }
            )
        ),
        401: openapi.Response(description="Unauthorized - Authentication required"),
        403: openapi.Response(description="Forbidden - Only Project Manager role can access this"),
    },
    tags=['Project Manager - Projects']
)
def get_all_projects_with_progress(request):
    """
    API endpoint for Project Manager to view all projects with progress tracking.
    Shows project progress, task counts, deadlines, and other details.
    
    Query Parameters:
    - status: Filter by project status (not_started, in_progress, completed, on_hold, cancelled)
    - search: Search in project name or client name
    
    Examples:
    - /api/project-manager/all-projects/ - Get all projects
    - /api/project-manager/all-projects/?status=completed - Get completed projects
    - /api/project-manager/all-projects/?status=in_progress - Get active projects
    - /api/project-manager/all-projects/?search=Office - Search for "Office"
    - /api/project-manager/all-projects/?status=in_progress&search=ABC - Combined filter
    """
    try:
        # Get all projects
        projects = Project.objects.all().order_by('-creating_date')
        
        # Apply status filter
        status_filter = request.query_params.get('status', '').strip()
        search_query = request.query_params.get('search', '').strip()
        
        filters_applied = {
            'status': status_filter if status_filter else None,
            'search': search_query if search_query else None,
        }
        
        valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
        if status_filter and status_filter in valid_statuses:
            projects = projects.filter(status=status_filter)
        
        # Apply search filter
        if search_query:
            projects = projects.filter(
                Q(project_name__icontains=search_query) |
                Q(client_name__icontains=search_query)
            )
        
        # Calculate status summary of ALL projects (not just filtered)
        all_projects = Project.objects.all()
        status_summary = {
            'not_started': all_projects.filter(status='not_started').count(),
            'in_progress': all_projects.filter(status='in_progress').count(),
            'completed': all_projects.filter(status='completed').count(),
            'on_hold': all_projects.filter(status='on_hold').count(),
            'cancelled': all_projects.filter(status='cancelled').count(),
        }
        
        # Calculate statistics for filtered projects
        total_projects = projects.count()
        completed_projects = projects.filter(status='completed').count()
        due_projects = projects.filter(
            end_date__lt=timezone.now().date(),
            status__in=['not_started', 'in_progress', 'on_hold']
        ).count()
        cancelled_projects = projects.filter(status='cancelled').count()
        in_progress_projects = projects.filter(status='in_progress').count()
        
        # Serialize the data
        from .serializers import ProjectManagerAssignedProjectSerializer
        serializer = ProjectManagerAssignedProjectSerializer(
            projects,
            many=True
        )
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {total_projects} projects",
                data={
                    'total_count': total_projects,
                    'filters_applied': filters_applied,
                    'status_summary': status_summary,
                    'statistics': {
                        'total_projects': total_projects,
                        'completed_projects': completed_projects,
                        'in_progress_projects': in_progress_projects,
                        'due_projects': due_projects,
                        'cancelled_projects': cancelled_projects,
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
                message=f"Error retrieving projects: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== COMPANY DASHBOARD API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="Company Dashboard - All Information",
    operation_description="""
    Complete company dashboard for Project Managers showing:
    - Overall project statistics
    - Weekly progress tracking
    - Completed vs In Progress projects
    - Progress rate and performance metrics
    - Task status distribution
    - Upcoming deadlines
    - Employee workload summary
    
    Returns comprehensive company performance data.
    """,
    responses={
        200: openapi.Response(
            description="Company dashboard data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'overall_stats': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
                                    'active_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
                                    'completed_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                    'on_hold_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                    'cancelled_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                }
                            ),
                            'task_stats': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=90),
                                    'completed_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=45),
                                    'in_progress_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=30),
                                    'not_started_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=15),
                                    'blocked_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                }
                            ),
                            'progress_rate': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'overall_progress': openapi.Schema(type=openapi.TYPE_NUMBER, example=50.0),
                                    'project_completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER, example=33.33),
                                    'task_completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER, example=50.0),
                                }
                            ),
                            'weekly_progress': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'week_start': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                    'week_end': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                    'tasks_completed_this_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'projects_completed_this_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'new_tasks_created_this_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'upcoming_deadlines': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'project_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'deadline': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                                        'tasks_completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    }
                                )
                            ),
                            'employee_summary': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_employees': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'active_employees': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'top_performers': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'employee_name': openapi.Schema(type=openapi.TYPE_STRING),
                                                'tasks_completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'active_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            }
                                        )
                                    ),
                                }
                            ),
                        }
                    )
                }
            )
        ),
    },
    tags=['Project Manager - Dashboard']
)
def company_dashboard(request):
    """
    Get comprehensive company dashboard with all statistics and metrics.
    """
    try:
        from django.db.models import Count, Q
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # ========== OVERALL STATS ==========
        all_projects = Project.objects.all()
        total_projects = all_projects.count()
        active_projects = all_projects.filter(status='in_progress').count()
        completed_projects = all_projects.filter(status='completed').count()
        on_hold_projects = all_projects.filter(status='on_hold').count()
        cancelled_projects = all_projects.filter(status='cancelled').count()
        
        # ========== TASK STATS ==========
        all_tasks = Task.objects.all()
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(status='completed').count()
        in_progress_tasks = all_tasks.filter(status='in_progress').count()
        not_started_tasks = all_tasks.filter(status='not_started').count()
        blocked_tasks = all_tasks.filter(status='blocked').count()
        
        # ========== PROGRESS RATES ==========
        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        project_completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # ========== WEEKLY PROGRESS ==========
        tasks_completed_this_week = Task.objects.filter(
            status='completed',
            updated_at__date__gte=week_start,
            updated_at__date__lte=week_end
        ).count()
        
        projects_completed_this_week = Project.objects.filter(
            status='completed',
            updated_at__date__gte=week_start,
            updated_at__date__lte=week_end
        ).count()
        
        new_tasks_created_this_week = Task.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        
        # ========== UPCOMING DEADLINES (All projects with end dates) ==========
        # Get all projects with end dates, sorted by closest deadline first
        upcoming_projects = Project.objects.filter(
            end_date__isnull=False
        ).exclude(
            status='completed'
        ).order_by('end_date')
        
        upcoming_deadlines = []
        for project in upcoming_projects:
            tasks = project.tasks.all()
            completed = tasks.filter(status='completed').count()
            total = tasks.count()
            
            # Calculate days remaining
            days_remaining = (project.end_date - today).days
            
            upcoming_deadlines.append({
                'project_id': project.id,
                'project_name': project.project_name,
                'client_name': project.client_name,
                'deadline': project.end_date.isoformat(),
                'days_remaining': days_remaining,
                'status': project.status,
                'tasks_completed': completed,
                'total_tasks': total,
                'progress_percentage': round((completed / total * 100), 2) if total > 0 else 0,
            })
        
        # ========== IN PROGRESS PROJECTS ==========
        in_progress_projects_query = Project.objects.filter(
            status='in_progress'
        ).order_by('-updated_at')
        
        in_progress_projects = []
        for project in in_progress_projects_query:
            tasks = project.tasks.all()
            completed = tasks.filter(status='completed').count()
            total = tasks.count()
            in_progress_count = tasks.filter(status='in_progress').count()
            
            # Calculate days remaining if end_date exists
            days_remaining = None
            if project.end_date:
                days_remaining = (project.end_date - today).days
            
            in_progress_projects.append({
                'project_id': project.id,
                'project_name': project.project_name,
                'client_name': project.client_name,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'days_remaining': days_remaining,
                'total_tasks': total,
                'completed_tasks': completed,
                'in_progress_tasks': in_progress_count,
                'progress_percentage': round((completed / total * 100), 2) if total > 0 else 0,
                'last_updated': project.updated_at.isoformat(),
            })
        
        # ========== EMPLOYEE SUMMARY ==========
        from authentication.models import User
        total_employees = User.objects.filter(role='Employee', company_name=request.user.company_name).count()
        active_employees = User.objects.filter(
            role='Employee',
            company_name=request.user.company_name,
            is_active=True
        ).count()
        
        # Top performers (employees with most completed tasks)
        top_performers_query = User.objects.filter(
            role='Employee',
            company_name=request.user.company_name
        ).annotate(
            completed_count=Count('assigned_tasks', filter=Q(assigned_tasks__status='completed')),
            active_count=Count('assigned_tasks', filter=Q(assigned_tasks__status='in_progress'))
        ).order_by('-completed_count')[:5]
        
        top_performers = []
        for employee in top_performers_query:
            top_performers.append({
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'tasks_completed': employee.completed_count,
                'active_tasks': employee.active_count,
            })
        
        # ========== COMPILE RESPONSE ==========
        dashboard_data = {
            'overall_stats': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'on_hold_projects': on_hold_projects,
                'cancelled_projects': cancelled_projects,
            },
            'task_stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'not_started_tasks': not_started_tasks,
                'blocked_tasks': blocked_tasks,
            },
            'progress_rate': {
                'overall_progress': round(overall_progress, 2),
                'project_completion_rate': round(project_completion_rate, 2),
                'task_completion_rate': round(task_completion_rate, 2),
            },
            'weekly_progress': {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'tasks_completed_this_week': tasks_completed_this_week,
                'projects_completed_this_week': projects_completed_this_week,
                'new_tasks_created_this_week': new_tasks_created_this_week,
            },
            'upcoming_deadlines': upcoming_deadlines,
            'in_progress_projects': in_progress_projects,
            'employee_summary': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'top_performers': top_performers,
            },
        }
        
        return Response(
            format_response(
                success=True,
                message="Company dashboard data retrieved successfully",
                data=dashboard_data
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving company dashboard: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== EMPLOYEE TIMESHEET API ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsProjectManager])
@swagger_auto_schema(
    operation_summary="View Company Employee Task Timers (Work Time Tracking)",
    operation_description="""
    API for Project Managers to view employee task timers for their company.
    Shows detailed work time tracking from the emopye app (employee timesheet module).
    
    Shows:
    - Employee name and work tracking
    - Task and project assignment
    - Work date and week range
    - Timer start/end times
    - Duration worked in seconds and formatted HH:MM:SS
    - Current duration for active timers
    - Timer status (active or completed)
    
    Query Parameters:
    - employee_id: Optional. Filter by specific employee ID
    - task_id: Optional. Filter by specific task ID
    - project_id: Optional. Filter by specific project ID
    - date: Optional. Filter by specific date (YYYY-MM-DD format)
    - start_date: Optional. Filter from start date (YYYY-MM-DD format)
    - end_date: Optional. Filter to end date (YYYY-MM-DD format)
    - week: Optional. Filter by week (format: YYYY-W##, e.g., 2025-W47 for week 47)
    - is_active: Optional. Filter by timer status (true/false, 1/0)
    
    Returns all task timers for company employees sorted by work_date descending.
    """,
    manual_parameters=[
        openapi.Parameter(
            'employee_id',
            openapi.IN_QUERY,
            description='Filter by specific employee ID',
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'task_id',
            openapi.IN_QUERY,
            description='Filter by specific task ID',
            type=openapi.TYPE_INTEGER,
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
            'date',
            openapi.IN_QUERY,
            description='Filter by specific date (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description='Filter from start date (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description='Filter to end date (YYYY-MM-DD)',
            type=openapi.TYPE_STRING,
            format='date',
            required=False
        ),
        openapi.Parameter(
            'week',
            openapi.IN_QUERY,
            description='Filter by week (format: YYYY-W##, e.g., 2025-W47)',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'is_active',
            openapi.IN_QUERY,
            description='Filter by timer status (true/false or 1/0, for running/stopped timers)',
            type=openapi.TYPE_STRING,
            required=False,
            enum=['true', 'false', '1', '0']
        ),
    ],
    responses={
        200: openapi.Response(
            description="Employee task timers retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_records': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_employees': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_working_hours': openapi.Schema(type=openapi.TYPE_STRING),
                            'timer_summary': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'active': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'timesheets': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                        'employee_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'employee_name': openapi.Schema(type=openapi.TYPE_STRING, example='John Smith'),
                                        'employee_email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'task_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'task_name': openapi.Schema(type=openapi.TYPE_STRING, example='Kitchen Design'),
                                        'project_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'project_name': openapi.Schema(type=openapi.TYPE_STRING, example='Office Renovation'),
                                        'client_name': openapi.Schema(type=openapi.TYPE_STRING, example='ABC Corp'),
                                        'work_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='2025-12-01'),
                                        'week': openapi.Schema(type=openapi.TYPE_STRING, example='01/12/2025 - 07/12/2025'),
                                        'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', nullable=True),
                                        'end_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', nullable=True),
                                        'duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, example=28800),
                                        'duration_formatted': openapi.Schema(type=openapi.TYPE_STRING, example='8 hours 0 minutes 0 seconds'),
                                        'current_duration_formatted': openapi.Schema(type=openapi.TYPE_STRING, example='8 hours 0 minutes 0 seconds'),
                                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                                    }
                                )
                            ),
                        }
                    )
                }
            )
        ),
    },
    tags=['Project Manager - Timesheet Management']
)
def view_company_timesheets(request):
    """
    Get all timesheets for company employees with optional filtering.
    """
    try:
        from datetime import datetime, timedelta
        from emopye.models import TaskTimer
        
        # Get all employees from the company
        company_employees = User.objects.filter(
            role='Employee',
            company_name=request.user.company_name
        )
        
        # Start with all task timers for company employees
        timesheets = TaskTimer.objects.filter(
            employee__in=company_employees
        ).select_related('employee', 'task', 'task__project').order_by('-work_date', '-start_time')
        
        # ========== FILTERS ==========
        
        # Filter by employee
        employee_id = request.query_params.get('employee_id', '').strip()
        if employee_id:
            timesheets = timesheets.filter(employee_id=employee_id)
        
        # Filter by specific date
        date_param = request.query_params.get('date', '').strip()
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                timesheets = timesheets.filter(work_date=filter_date)
            except ValueError:
                pass
        
        # Filter by date range
        start_date_param = request.query_params.get('start_date', '').strip()
        end_date_param = request.query_params.get('end_date', '').strip()
        
        if start_date_param:
            try:
                start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
                timesheets = timesheets.filter(work_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date_param:
            try:
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
                timesheets = timesheets.filter(work_date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by week (ISO week format: YYYY-W##)
        week_param = request.query_params.get('week', '').strip()
        if week_param:
            try:
                # Parse week format (e.g., 2025-W47)
                year, week = week_param.split('-W')
                year = int(year)
                week = int(week)
                
                # Calculate Monday of the week
                jan_4 = timezone.now().replace(year=year, month=1, day=4)
                week_one_monday = jan_4 - timedelta(days=jan_4.weekday())
                week_monday = week_one_monday + timedelta(weeks=week-1)
                week_sunday = week_monday + timedelta(days=6)
                
                timesheets = timesheets.filter(
                    work_date__gte=week_monday.date(),
                    work_date__lte=week_sunday.date()
                )
            except (ValueError, AttributeError):
                pass
        
        # Filter by task
        task_id = request.query_params.get('task_id', '').strip()
        if task_id:
            timesheets = timesheets.filter(task_id=task_id)
        
        # Filter by project
        project_id = request.query_params.get('project_id', '').strip()
        if project_id:
            timesheets = timesheets.filter(task__project_id=project_id)
        
        # Filter by is_active status
        is_active_param = request.query_params.get('is_active', '').strip()
        if is_active_param.lower() in ['true', '1']:
            timesheets = timesheets.filter(is_active=True)
        elif is_active_param.lower() in ['false', '0']:
            timesheets = timesheets.filter(is_active=False)
        
        # ========== CALCULATE STATISTICS ==========
        total_records = timesheets.count()
        unique_employees = timesheets.values('employee_id').distinct().count()
        
        # Timer status summary
        active_timers = timesheets.filter(is_active=True).count()
        completed_timers = timesheets.filter(is_active=False).count()
        
        # Total working hours
        total_duration = timedelta()
        for timer in timesheets:
            total_duration += timedelta(seconds=timer.duration_seconds)
        
        total_seconds = int(total_duration.total_seconds())
        total_hours = total_seconds // 3600
        total_minutes = (total_seconds % 3600) // 60
        total_working_hours = f"{total_hours} hours {total_minutes} minutes"
        
        # ========== FORMAT TIMESHEET DATA ==========
        timesheet_list = []
        for timer in timesheets:
            # Calculate week range for each date
            work_date = timer.work_date
            week_start = work_date - timedelta(days=work_date.weekday())
            week_end = week_start + timedelta(days=6)
            week_range = f"{week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
            
            # Format duration
            hours = timer.duration_seconds // 3600
            minutes = (timer.duration_seconds % 3600) // 60
            seconds = timer.duration_seconds % 60
            duration_str = f"{hours} hours {minutes} minutes {seconds} seconds"
            
            # Get current duration for active timers
            if timer.is_active and timer.start_time:
                current_duration = int((timezone.now() - timer.start_time).total_seconds())
                current_hours = current_duration // 3600
                current_minutes = (current_duration % 3600) // 60
                current_seconds = current_duration % 60
                current_duration_str = f"{current_hours} hours {current_minutes} minutes {current_seconds} seconds"
            else:
                current_duration_str = duration_str
            
            timesheet_list.append({
                'id': timer.id,
                'employee_id': timer.employee.id,
                'employee_name': f"{timer.employee.first_name} {timer.employee.last_name}",
                'employee_email': timer.employee.email,
                'task_id': timer.task.id,
                'task_name': timer.task.task_name,
                'project_id': timer.task.project.id,
                'project_name': timer.task.project.project_name,
                'client_name': timer.task.project.client_name,
                'work_date': timer.work_date.isoformat(),
                'week': week_range,
                'start_time': timer.start_time.isoformat() if timer.start_time else None,
                'end_time': timer.end_time.isoformat() if timer.end_time else None,
                'duration_seconds': timer.duration_seconds,
                'duration_formatted': duration_str,
                'current_duration_formatted': current_duration_str,
                'is_active': timer.is_active,
                'created_at': timer.created_at.isoformat(),
                'updated_at': timer.updated_at.isoformat(),
            })
        
        # ========== COMPILE RESPONSE ==========
        response_data = {
            'total_records': total_records,
            'total_employees': unique_employees,
            'total_working_hours': total_working_hours,
            'timer_summary': {
                'active': active_timers,
                'completed': completed_timers,
            },
            'timesheets': timesheet_list,
        }
        
        return Response(
            format_response(
                success=True,
                message=f"Retrieved {total_records} timesheet records for {unique_employees} employees",
                data=response_data
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving employee timesheets: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
