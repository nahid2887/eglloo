from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import TimeEntry
from .serializers import (
    TimeEntrySerializer,
    StartTimeSerializer,
    EndTimeSerializer,
    WeeklyHoursSerializer,
    AttendanceSummarySerializer
)


class StartTimeView(APIView):
    """
    API endpoint for employee to start their work time (clock in)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=StartTimeSerializer,
        responses={
            201: openapi.Response(
                description="Time entry started successfully",
                schema=TimeEntrySerializer
            ),
            400: "Bad Request - Entry already exists for today",
        },
        operation_description="Employee clocks in - Start work time for the day"
    )
    def post(self, request):
        serializer = StartTimeSerializer(data=request.data)
        if serializer.is_valid():
            entry_time = serializer.validated_data['entry_time']
            date = serializer.validated_data['date']
            
            # Check if entry already exists for today
            existing_entry = TimeEntry.objects.filter(
                user=request.user,
                date=date
            ).first()
            
            if existing_entry and existing_entry.entry_time:
                return Response({
                    'error': 'You have already clocked in today',
                    'existing_entry': TimeEntrySerializer(existing_entry).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or update time entry
            if existing_entry:
                existing_entry.entry_time = entry_time
                existing_entry.save()
                time_entry = existing_entry
            else:
                time_entry = TimeEntry.objects.create(
                    user=request.user,
                    date=date,
                    entry_time=entry_time,
                    attendance='Absent'  # Will be updated when exit time is set
                )
            
            return Response({
                'message': 'Clocked in successfully',
                'entry': TimeEntrySerializer(time_entry).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EndTimeView(APIView):
    """
    API endpoint for employee to end their work time (clock out)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=EndTimeSerializer,
        responses={
            200: openapi.Response(
                description="Time entry ended successfully",
                schema=TimeEntrySerializer
            ),
            400: "Bad Request - No entry time found for today",
        },
        operation_description="Employee clocks out - End work time and calculate total hours"
    )
    def post(self, request):
        serializer = EndTimeSerializer(data=request.data)
        if serializer.is_valid():
            exit_time = serializer.validated_data['exit_time']
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
                    'entry': TimeEntrySerializer(time_entry).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set exit time and calculate working time
            time_entry.exit_time = exit_time
            time_entry.save()  # This will trigger calculate_working_time()
            
            return Response({
                'message': 'Clocked out successfully',
                'entry': TimeEntrySerializer(time_entry).data,
                'total_working_time': time_entry.get_working_hours(),
                'attendance': time_entry.attendance
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTimeEntryView(APIView):
    """
    API endpoint to update time entry (for corrections)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Date of entry (YYYY-MM-DD)'),
                'entry_time': openapi.Schema(type=openapi.TYPE_STRING, format='time', description='Start time (HH:MM:SS)'),
                'exit_time': openapi.Schema(type=openapi.TYPE_STRING, format='time', description='End time (HH:MM:SS)'),
            }
        ),
        responses={
            200: TimeEntrySerializer,
            400: "Bad Request",
        },
        operation_description="Update time entry for corrections"
    )
    def patch(self, request, entry_id):
        try:
            time_entry = TimeEntry.objects.get(id=entry_id, user=request.user)
        except TimeEntry.DoesNotExist:
            return Response({
                'error': 'Time entry not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields if provided
        if 'entry_time' in request.data:
            time_entry.entry_time = request.data['entry_time']
        
        if 'exit_time' in request.data:
            time_entry.exit_time = request.data['exit_time']
        
        time_entry.save()  # This will recalculate working time
        
        return Response({
            'message': 'Time entry updated successfully',
            'entry': TimeEntrySerializer(time_entry).data
        }, status=status.HTTP_200_OK)


class MyTimeEntriesView(generics.ListAPIView):
    """
    API endpoint to get all time entries for the logged-in user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter from date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter to date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={200: TimeEntrySerializer(many=True)},
        operation_description="Get all time entries for logged-in employee with optional date filters"
    )
    def get(self, request, *args, **kwargs):
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


class WeeklyHoursView(APIView):
    """
    API endpoint to get weekly working hours summary
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Week start date (YYYY-MM-DD), defaults to current week", type=openapi.TYPE_STRING),
        ],
        responses={200: WeeklyHoursSerializer},
        operation_description="Get total working hours for the week with daily breakdown"
    )
    def get(self, request):
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
            'entries': TimeEntrySerializer(weekly_data['entries'], many=True).data
        }, status=status.HTTP_200_OK)


class TodayStatusView(APIView):
    """
    API endpoint to get today's time entry status
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: TimeEntrySerializer},
        operation_description="Get today's time entry status (clocked in/out status)"
    )
    def get(self, request):
        today = timezone.now().date()
        time_entry = TimeEntry.objects.filter(
            user=request.user,
            date=today
        ).first()
        
        if time_entry:
            return Response({
                'has_clocked_in': bool(time_entry.entry_time),
                'has_clocked_out': bool(time_entry.exit_time),
                'entry': TimeEntrySerializer(time_entry).data
            })
        
        return Response({
            'has_clocked_in': False,
            'has_clocked_out': False,
            'entry': None
        })


# ========== ADMIN VIEWS ==========

class AllEmployeeTimeEntriesView(generics.ListAPIView):
    """
    API endpoint for admin to view all employees' time entries
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        # Only admins can view all entries
        if self.request.user.role != 'Admin':
            return TimeEntry.objects.filter(user=self.request.user)
        
        return TimeEntry.objects.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="Filter by user ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter from date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter to date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('attendance', openapi.IN_QUERY, description="Filter by attendance status", type=openapi.TYPE_STRING),
        ],
        responses={200: TimeEntrySerializer(many=True)},
        operation_description="Admin can view all employees' time entries with filters"
    )
    def get(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            return Response({
                'error': 'Only admins can view all employee time entries'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Apply filters
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        attendance = request.query_params.get('attendance')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if attendance:
            queryset = queryset.filter(attendance=attendance)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

