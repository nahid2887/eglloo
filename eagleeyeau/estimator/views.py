from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import Estimate
from .serializers import EstimateSerializer, EstimateListSerializer


class EstimateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for complete Estimate management.
    
    Endpoints:
    - POST /api/estimator/estimates/ - Create estimate with all items
    - GET /api/estimator/estimates/ - List all estimates with counts
    - GET /api/estimator/estimates/{id}/ - Get single estimate
    - PUT/PATCH /api/estimator/estimates/{id}/ - Update estimate
    - DELETE /api/estimator/estimates/{id}/ - Delete estimate
    
    Status Workflow:
    - POST /api/estimator/estimates/{id}/send_for_approval/ - Send for approval
    - POST /api/estimator/estimates/{id}/approve/ - Approve estimate
    - POST /api/estimator/estimates/{id}/reject/ - Reject estimate
    """
    
    queryset = Estimate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return EstimateListSerializer
        return EstimateSerializer
    
    def list(self, request, *args, **kwargs):
        """List estimates with status counts"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get counts
        total = queryset.count()
        pending = queryset.filter(status='pending').count()
        sent = queryset.filter(status='sent').count()
        approved = queryset.filter(status='approved').count()
        rejected = queryset.filter(status='rejected').count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data = {
                'counts': {
                    'total': total,
                    'pending': pending,
                    'sent': sent,
                    'approved': approved,
                    'rejected': rejected,
                },
                'results': response.data
            }
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'counts': {
                'total': total,
                'pending': pending,
                'sent': sent,
                'approved': approved,
                'rejected': rejected,
            },
            'results': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Create estimate with all items in single API call"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set created_by to current user
        estimate = serializer.save(created_by=request.user)
        
        return Response(
            EstimateSerializer(estimate).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def send_for_approval(self, request, pk=None):
        """Send estimate for approval (pending -> sent)"""
        estimate = self.get_object()
        
        if estimate.status != 'pending':
            return Response(
                {'error': f'Estimate must be in pending status. Current: {estimate.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate.status = 'sent'
        estimate.save()
        
        return Response({
            'message': 'Estimate sent for approval',
            'status': estimate.status
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve estimate (sent -> approved)"""
        estimate = self.get_object()
        
        if estimate.status != 'sent':
            return Response(
                {'error': f'Estimate must be in sent status. Current: {estimate.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate.status = 'approved'
        estimate.save()
        
        return Response({
            'message': 'Estimate approved',
            'status': estimate.status
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject estimate (sent -> rejected)"""
        estimate = self.get_object()
        
        if estimate.status != 'sent':
            return Response(
                {'error': f'Estimate must be in sent status. Current: {estimate.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimate.status = 'rejected'
        estimate.save()
        
        return Response({
            'message': 'Estimate rejected',
            'status': estimate.status
        })
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get estimates filtered by status"""
        status_filter = request.query_params.get('status')
        
        if not status_filter:
            return Response(
                {'error': 'status query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status_filter)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': status_filter,
            'count': queryset.count(),
            'results': serializer.data
        })
