from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import TimeEntry
from .serializers import (
    EmployeeTimeEntrySerializer,
    StartTimeSerializer,
    EndTimeSerializer,
    WeeklyHoursSerializer,
)
from eagleeyeau.response_formatter import format_response
from eagleeyeau.api_messages import EMPLOYEE_MESSAGES, PERMISSION_MESSAGES


class IsEmployee(IsAuthenticated):
    """Permission class to check if user is Employee role"""
    
    def has_permission(self, request, view):
        # First check if authenticated
        if not super().has_permission(request, view):
            return False
        
        # Check if user has Employee role
        return request.user.role == 'Employee'


class EmployeeStartTimeView(APIView):
    """
    API endpoint for EMPLOYEE ONLY to clock in (start work time)
    Uses current time automatically
    """
    permission_classes = [IsEmployee]

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Clocked in successfully",
                schema=EmployeeTimeEntrySerializer
            ),
            400: "Bad Request - Already clocked in",
            403: "Forbidden - Only Employee role can access"
        },
        operation_description="Employee clocks in - Uses current time automatically (Employee role only)"
    )
    def post(self, request):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can clock in',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Use current time
        current_time = timezone.now().time()
        today = timezone.now().date()
        
        # Check if entry already exists for today
        existing_entry = TimeEntry.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if existing_entry and existing_entry.entry_time:
            return Response({
                'error': 'You have already clocked in today',
                'existing_entry': EmployeeTimeEntrySerializer(existing_entry).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update time entry
        if existing_entry:
            existing_entry.entry_time = current_time
            existing_entry.save()
            time_entry = existing_entry
        else:
            time_entry = TimeEntry.objects.create(
                user=request.user,
                date=today,
                entry_time=current_time,
                attendance='Absent'  # Will be updated when exit time is set
            )
        
        return Response({
            'message': 'Clocked in successfully',
            'entry': EmployeeTimeEntrySerializer(time_entry).data
        }, status=status.HTTP_201_CREATED)


class EmployeeEndTimeView(APIView):
    """
    API endpoint for EMPLOYEE ONLY to clock out (end work time)
    Uses current time automatically
    """
    permission_classes = [IsEmployee]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Clocked out successfully",
                schema=EmployeeTimeEntrySerializer
            ),
            400: "Bad Request - Not clocked in or already clocked out",
            403: "Forbidden - Only Employee role can access"
        },
        operation_description="Employee clocks out - Uses current time automatically (Employee role only)"
    )
    def post(self, request):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can clock out',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Use current time
        current_time = timezone.now().time()
        today = timezone.now().date()
        
        # Find today's entry
        time_entry = TimeEntry.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if not time_entry or not time_entry.entry_time:
            return Response({
                'error': 'You must clock in first before clocking out'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if time_entry.exit_time:
            return Response({
                'error': 'You have already clocked out today',
                'entry': EmployeeTimeEntrySerializer(time_entry).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set exit time and calculate working time
        time_entry.exit_time = current_time
        time_entry.save()  # This will trigger calculate_working_time()
        
        return Response({
            'message': 'Clocked out successfully',
            'entry': EmployeeTimeEntrySerializer(time_entry).data,
            'total_working_time': time_entry.get_working_hours(),
            'attendance': time_entry.attendance
        }, status=status.HTTP_200_OK)


class EmployeeMyTimeEntriesView(generics.ListAPIView):
    """
    API endpoint for EMPLOYEE to view their own time entries only
    """
    permission_classes = [IsEmployee]
    serializer_class = EmployeeTimeEntrySerializer

    def get_queryset(self):
        # Only return logged-in employee's entries
        return TimeEntry.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter from date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter to date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: EmployeeTimeEntrySerializer(many=True),
            403: "Forbidden - Only Employee role can access"
        },
        operation_description="Get own time entries (Employee role only)"
    )
    def get(self, request, *args, **kwargs):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can view time entries',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeWeeklyHoursView(APIView):
    """
    API endpoint for EMPLOYEE to view their own weekly hours
    """
    permission_classes = [IsEmployee]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Week start date (YYYY-MM-DD), defaults to current week", type=openapi.TYPE_STRING),
        ],
        responses={
            200: WeeklyHoursSerializer,
            403: "Forbidden - Only Employee role can access"
        },
        operation_description="Get own weekly working hours (Employee role only)"
    )
    def get(self, request):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can view weekly hours',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        start_date = request.query_params.get('start_date')
        
        if start_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        weekly_data = TimeEntry.get_weekly_hours(request.user, start_date)
        
        return Response({
            'week_start': start_date or (timezone.now().date() - timezone.timedelta(days=timezone.now().date().weekday())),
            'total_hours': weekly_data['total_hours'],
            'total_minutes': weekly_data['total_minutes'],
            'formatted': weekly_data['formatted'],
            'entries': EmployeeTimeEntrySerializer(weekly_data['entries'], many=True).data
        }, status=status.HTTP_200_OK)


class EmployeeTodayStatusView(APIView):
    """
    API endpoint for EMPLOYEE to view today's status
    """
    permission_classes = [IsEmployee]

    @swagger_auto_schema(
        responses={
            200: EmployeeTimeEntrySerializer,
            403: "Forbidden - Only Employee role can access"
        },
        operation_description="Get today's clock in/out status (Employee role only)"
    )
    def get(self, request):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can view today status',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now().date()
        time_entry = TimeEntry.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if time_entry:
            return Response({
                'has_clocked_in': bool(time_entry.entry_time),
                'has_clocked_out': bool(time_entry.exit_time),
                'entry': EmployeeTimeEntrySerializer(time_entry).data
            })
        
        return Response({
            'has_clocked_in': False,
            'has_clocked_out': False,
            'entry': None
        })


class EmployeeDashboardView(APIView):
    """
    API endpoint for EMPLOYEE dashboard - Shows own data only
    """
    permission_classes = [IsEmployee]

    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Employee dashboard data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'role': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    'hours_this_week': openapi.Schema(type=openapi.TYPE_STRING),
                    'today_entry': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'this_week_entries': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'week_start': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'week_end': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                }
            )
        )},
        operation_description="Get employee dashboard with own data only (Employee role only)"
    )
    def get(self, request):
        # Check if user is Employee
        if request.user.role != 'Employee':
            return Response({
                'error': 'Only users with Employee role can view dashboard',
                'your_role': request.user.role
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get weekly hours
        weekly_data = TimeEntry.get_weekly_hours(request.user)
        
        # Get today's entry
        today = timezone.now().date()
        today_entry = TimeEntry.objects.filter(user=request.user, date=today).first()
        
        # Get this week's entries
        week_start = today - timezone.timedelta(days=today.weekday())
        week_end = week_start + timezone.timedelta(days=6)
        week_entries = TimeEntry.objects.filter(
            user=request.user,
            date__range=[week_start, week_end]
        )
        
        return Response({
            'user': {
                'email': request.user.email,
                'name': f"{request.user.first_name} {request.user.last_name}",
                'role': request.user.role
            },
            'hours_this_week': weekly_data['formatted'],
            'today_entry': EmployeeTimeEntrySerializer(today_entry).data if today_entry else None,
            'this_week_entries': EmployeeTimeEntrySerializer(week_entries, many=True).data,
            'week_start': week_start,
            'week_end': week_end
        }, status=status.HTTP_200_OK)

