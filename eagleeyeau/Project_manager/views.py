from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from eagleeyeau.response_formatter import format_response
from authentication.models import User
from timesheet.models import TimeEntry
from .serializers import EmployeeSerializer, TimeEntrySerializer, EmployeeTimesheetDetailSerializer


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
def get_company_employees(request):
    """
    API endpoint for Project Manager to view all Employee role users from the same company.
    
    Endpoint: GET /api/project-manager/employees/
    
    Returns:
    - List of all Employee users from the same company as the logged-in user
    - Only accessible by Project Manager or Admin users
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
        ).order_by('first_name', 'last_name')
        
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
