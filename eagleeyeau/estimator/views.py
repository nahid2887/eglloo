from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Estimate
from .serializers import EstimateSerializer, EstimateListSerializer
from eagleeyeau.response_formatter import format_response


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
    
    def get_queryset(self):
        """
        Filter estimates based on user role:
        - Estimators see only their own estimates
        - Admins see all estimates
        """
        user = self.request.user
        is_admin = user.role == 'Admin' if hasattr(user, 'role') else user.is_staff
        
        if is_admin:
            return Estimate.objects.all().order_by('-created_at')
        else:
            # Estimators see only their own estimates
            return Estimate.objects.filter(created_by=user).order_by('-created_at')
    
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
    
    @swagger_auto_schema(
        operation_summary="Create estimate with multiple items",
        operation_description="""
        Create a new estimate with multiple items in a single API call.
        
        KEY POINT: Each item has ONE item_type (material, component, or estimate_default).
        You can add as many items as needed - each with its own type, quantity, price, and notes.
        
        Item Structure:
        - item_type: 'material' | 'component' | 'estimate_default'
        - item_id: ID of the item in database
        - quantity: Quantity of this item
        - unit_price: Price per unit for this estimate
        - notes: Optional notes for this specific item
        
        Response includes:
        - item_total_cost: Calculated as quantity × unit_price
        - item_details: Complete data for the referenced item
        
        Example: An estimate can have:
        - 2x Material items (different materials)
        - 1x Component item
        - 1x EstimateDefault item
        Total: 4 items in the same estimate
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['serial_number', 'client_name', 'project_name', 'items'],
            properties={
                'serial_number': openapi.Schema(type=openapi.TYPE_STRING, description='Unique serial number'),
                'estimate_number': openapi.Schema(type=openapi.TYPE_STRING, description='Estimate number (optional)'),
                'client_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the client'),
                'project_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                'profit_margin': openapi.Schema(type=openapi.TYPE_NUMBER, description='Profit margin percentage'),
                'income_tax': openapi.Schema(type=openapi.TYPE_NUMBER, description='Income tax percentage'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='End/completion date of the project (optional)'),
                'targeted_rooms': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='Array of targeted rooms (optional)'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Additional notes'),
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=['item_type', 'item_id', 'quantity', 'unit_price'],
                        properties={
                            'item_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['material', 'component', 'estimate_default']),
                            'item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the item'),
                            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity'),
                            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Price per unit'),
                            'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Item notes'),
                        }
                    )
                ),
            },
            example={
                'serial_number': 'EST-2025-001',
                'estimate_number': 'EST-2025-CLIENT-001',
                'client_name': 'Acme Corporation',
                'project_name': 'Office Renovation',
                'end_date': '2025-12-31',
                'targeted_rooms': ['Conference Room', 'Meeting Room B'],
                'profit_margin': 15.0,
                'income_tax': 8.0,
                'notes': 'Detailed project notes',
                'items': [
                    {
                        'item_type': 'material',
                        'item_id': 1,
                        'quantity': 5,
                        'unit_price': 100.00,
                        'notes': 'High quality material'
                    },
                    {
                        'item_type': 'component',
                        'item_id': 2,
                        'quantity': 2,
                        'unit_price': 250.00,
                        'notes': 'Standard component'
                    },
                    {
                        'item_type': 'estimate_default',
                        'item_id': 1,
                        'quantity': 1,
                        'unit_price': 500.00,
                        'notes': 'Custom service'
                    }
                ]
            }
        ),
        responses={201: EstimateSerializer},
        tags=['Estimates']
    )
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
    
    @swagger_auto_schema(
        operation_summary="Send estimate for approval",
        operation_description="Change estimate status from 'pending' to 'sent' for approval workflow.",
        tags=['Estimates']
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
    
    @swagger_auto_schema(
        operation_summary="Approve estimate",
        operation_description="Change estimate status from 'sent' to 'approved'.",
        tags=['Estimates']
    )
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
    
    @swagger_auto_schema(
        operation_summary="Reject estimate",
        operation_description="Change estimate status from 'sent' to 'rejected'.",
        tags=['Estimates']
    )
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
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        operation_summary="Download estimate as PDF",
        operation_description="Download complete estimate information as a PDF file with all items, pricing, and totals.",
        responses={200: openapi.Response(description="PDF file with estimate information")},
        tags=['Estimates']
    )
    def download_pdf(self, request, pk=None):
        """Download estimate as PDF"""
        try:
            estimate = self.get_object()
            pdf_content = self._generate_estimate_pdf(estimate)
            
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
            filename = f"Estimate_{estimate.serial_number}.pdf"
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
                    message=f"Error downloading estimate: {str(e)}",
                    data=None
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_estimate_pdf(self, estimate):
        """Generate PDF of the estimate with all details"""
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
                fontSize=22,
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
            elements.append(Paragraph(f"ESTIMATE: {estimate.serial_number}", title_style))
            if estimate.estimate_number:
                elements.append(Paragraph(f"Estimate #: {estimate.estimate_number}", styles['Normal']))
            elements.append(Spacer(1, 0.15 * inch))
            
            # ===== ESTIMATE DETAILS =====
            elements.append(Paragraph("ESTIMATE DETAILS", heading_style))
            details_data = [
                ['Field', 'Value'],
                ['Client Name', estimate.client_name or 'N/A'],
                ['Project Name', estimate.project_name or 'N/A'],
                ['Serial Number', estimate.serial_number],
                ['Status', estimate.status.replace('_', ' ').title()],
                ['Created Date', estimate.estimate_date.strftime('%Y-%m-%d') if estimate.estimate_date else 'N/A'],
                ['End Date', estimate.end_date.strftime('%Y-%m-%d') if estimate.end_date else 'N/A'],
                ['Created By', estimate.created_by.email if estimate.created_by else 'System'],
            ]
            
            details_table = Table(details_data, colWidths=[1.8*inch, 3.7*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(details_table)
            elements.append(Spacer(1, 0.15 * inch))
            
            # ===== ITEMS TABLE =====
            if estimate.items:
                elements.append(Paragraph("ESTIMATE ITEMS", heading_style))
                
                items_data = [
                    ['Item Type', 'Item', 'Qty', 'Unit Price', 'Item Total', 'Notes']
                ]
                
                for item in estimate.items:
                    item_type = item.get('item_type', 'N/A')
                    item_id = item.get('item_id', 'N/A')
                    quantity = item.get('quantity', 0)
                    unit_price = item.get('unit_price', 0)
                    item_total = quantity * unit_price
                    notes = item.get('notes', '')[:50]
                    
                    items_data.append([
                        item_type.title(),
                        f"ID: {item_id}",
                        str(quantity),
                        f"${float(unit_price):,.2f}",
                        f"${item_total:,.2f}",
                        notes or '-'
                    ])
                
                items_table = Table(items_data, colWidths=[0.9*inch, 0.8*inch, 0.6*inch, 1.1*inch, 1.1*inch, 1.4*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(items_table)
                elements.append(Spacer(1, 0.2 * inch))
            
            # ===== PRICING SUMMARY =====
            elements.append(Paragraph("PRICING SUMMARY", heading_style))
            
            total_cost = estimate.total_cost
            profit_margin = estimate.profit_margin
            total_with_profit = estimate.total_with_profit
            tax = estimate.income_tax
            total_with_tax = estimate.total_with_tax
            
            pricing_data = [
                ['Description', 'Amount'],
                ['Subtotal', f"${total_cost:,.2f}"],
                [f'Profit Margin ({profit_margin}%)', f"${total_with_profit - total_cost:,.2f}"],
                ['Subtotal with Profit', f"${total_with_profit:,.2f}"],
                [f'Tax ({tax}%)', f"${total_with_tax - total_with_profit:,.2f}"],
                ['TOTAL AMOUNT', f"${total_with_tax:,.2f}"],
            ]
            
            pricing_table = Table(pricing_data, colWidths=[3.25*inch, 2.25*inch])
            pricing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f0f8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4e6f1')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(pricing_table)
            elements.append(Spacer(1, 0.2 * inch))
            
            # ===== ROOMS =====
            if estimate.targeted_rooms:
                elements.append(Paragraph("TARGETED ROOMS", heading_style))
                rooms_text = ', '.join(estimate.targeted_rooms) if isinstance(estimate.targeted_rooms, list) else str(estimate.targeted_rooms)
                elements.append(Paragraph(rooms_text, styles['BodyText']))
                elements.append(Spacer(1, 0.15 * inch))
            
            # ===== NOTES =====
            if estimate.notes:
                elements.append(Paragraph("NOTES", heading_style))
                elements.append(Paragraph(estimate.notes, styles['BodyText']))
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
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Lignaflow Estimating System",
                footer_style
            ))
            
            # Build PDF
            doc.build(elements)
            return buffer.getvalue()
        
        except ImportError:
            return None
        except Exception as e:
            return None
    
    @swagger_auto_schema(
        operation_summary="Get estimates by status",
        operation_description="Filter estimates by status (pending, sent, approved, rejected).",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description='Filter by status', type=openapi.TYPE_STRING, required=True),
        ],
        tags=['Estimates']
    )
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
    
    @swagger_auto_schema(
        operation_summary="Delete estimate",
        operation_description="Delete an estimate. Estimators can only delete their own estimates (created_by must match current user). Admins can delete any estimate.",
        responses={
            204: openapi.Response(description="Estimate deleted successfully"),
            403: openapi.Response(description="Permission denied - You can only delete your own estimates"),
            404: openapi.Response(description="Estimate not found"),
            500: openapi.Response(description="Server error")
        },
        tags=['Estimates']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an estimate - only owner can delete"""
        try:
            estimate = self.get_object()
            
            # Check if user is the creator of the estimate or is admin
            is_admin = request.user.role == 'Admin' if hasattr(request.user, 'role') else request.user.is_staff
            is_owner = estimate.created_by == request.user
            
            if not (is_owner or is_admin):
                return Response(
                    {'error': 'You can only delete your own estimates'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            estimate_id = estimate.id
            serial_number = estimate.serial_number
            estimate_number = estimate.estimate_number or 'N/A'
            
            # Delete the estimate
            estimate.delete()
            
            return Response(
                {
                    'message': f"Estimate (ID: {estimate_id}, Serial: {serial_number}, Number: {estimate_number}) deleted successfully",
                    'deleted_id': estimate_id
                },
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Estimate.DoesNotExist:
            return Response(
                {'error': 'Estimate not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================== ESTIMATOR DASHBOARD API ======================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_summary="Estimator Dashboard Overview",
    operation_description="""
    Complete estimator dashboard showing:
    - Estimates Due Soon (sorted by end_date, closest first)
    - Recent Estimates (created recently)
    - Completed Estimates (status: approved)
    - Overview statistics (counts by status)
    - Performance metrics (estimated value by status)
    
    Returns comprehensive dashboard data for estimators to track their estimates.
    """,
    responses={
        200: openapi.Response(
            description="Dashboard data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'overview': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_estimates': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'sent': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'approved': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'rejected': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            ),
                            'value_summary': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'pending_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'sent_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'approved_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'rejected_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'total_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                                }
                            ),
                            'due_soon': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                description="Estimates with end_date within next 30 days, sorted by closest deadline"
                            ),
                            'recent_estimates': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                description="Last 10 created estimates"
                            ),
                            'completed_estimates': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                description="Approved estimates"
                            ),
                            'performance': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'approval_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage of approved estimates'),
                                    'rejection_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage of rejected estimates'),
                                    'pending_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage of pending estimates'),
                                    'average_estimate_value': openapi.Schema(type=openapi.TYPE_NUMBER, description='Average value per estimate'),
                                }
                            ),
                        }
                    )
                }
            )
        ),
    },
    tags=['Estimator - Dashboard']
)
def estimator_dashboard(request):
    """
    Get comprehensive estimator dashboard with all statistics, recent estimates, and due soon estimates.
    
    Endpoint: GET /api/estimator/dashboard/
    
    Returns:
    - Overview: Total count and breakdown by status
    - Value Summary: Total estimated value by status
    - Due Soon: Estimates with end_date within next 30 days
    - Recent Estimates: Last 10 created estimates
    - Completed Estimates: All approved estimates
    - Performance Metrics: Approval rate, rejection rate, average value
    
    Example: /api/estimator/dashboard/
    """
    try:
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        # Get user's estimates (Estimators see only their own)
        is_admin = request.user.role == 'Admin' if hasattr(request.user, 'role') else request.user.is_staff
        
        if is_admin:
            all_estimates = Estimate.objects.all()
        else:
            all_estimates = Estimate.objects.filter(created_by=request.user)
        
        # ========== OVERVIEW STATISTICS ==========
        total_estimates = all_estimates.count()
        pending_count = all_estimates.filter(status='pending').count()
        sent_count = all_estimates.filter(status='sent').count()
        approved_count = all_estimates.filter(status='approved').count()
        rejected_count = all_estimates.filter(status='rejected').count()
        
        # ========== VALUE SUMMARY ==========
        # Calculate total value for each status by summing total_with_tax for each estimate
        pending_estimates = all_estimates.filter(status='pending')
        sent_estimates = all_estimates.filter(status='sent')
        approved_estimates = all_estimates.filter(status='approved')
        rejected_estimates = all_estimates.filter(status='rejected')
        
        pending_value = sum([float(est.total_with_tax) for est in pending_estimates])
        sent_value = sum([float(est.total_with_tax) for est in sent_estimates])
        approved_value = sum([float(est.total_with_tax) for est in approved_estimates])
        rejected_value = sum([float(est.total_with_tax) for est in rejected_estimates])
        total_value = pending_value + sent_value + approved_value + rejected_value
        
        # ========== DUE SOON (Next 30 days) ==========
        due_soon = all_estimates.filter(
            end_date__isnull=False,
            end_date__gte=today,
            end_date__lte=thirty_days_later
        ).order_by('end_date')[:10]
        
        due_soon_data = []
        for estimate in due_soon:
            days_remaining = (estimate.end_date - today).days
            due_soon_data.append({
                'id': estimate.id,
                'serial_number': estimate.serial_number,
                'estimate_number': estimate.estimate_number,
                'project_name': estimate.project_name,
                'client_name': estimate.client_name,
                'end_date': estimate.end_date.isoformat(),
                'days_remaining': days_remaining,
                'status': estimate.status,
                'total_value': float(estimate.total_with_tax),
            })
        
        # ========== RECENT ESTIMATES (Last 10) ==========
        recent_estimates = all_estimates.order_by('-created_at')[:10]
        
        recent_data = []
        for estimate in recent_estimates:
            recent_data.append({
                'id': estimate.id,
                'serial_number': estimate.serial_number,
                'estimate_number': estimate.estimate_number,
                'project_name': estimate.project_name,
                'client_name': estimate.client_name,
                'status': estimate.status,
                'created_at': estimate.created_at.isoformat(),
                'total_value': float(estimate.total_with_tax),
                'estimate_date': estimate.estimate_date.isoformat(),
            })
        
        # ========== COMPLETED ESTIMATES (Approved) ==========
        completed_estimates = all_estimates.filter(status='approved').order_by('-updated_at')
        
        completed_data = []
        for estimate in completed_estimates:
            completed_data.append({
                'id': estimate.id,
                'serial_number': estimate.serial_number,
                'estimate_number': estimate.estimate_number,
                'project_name': estimate.project_name,
                'client_name': estimate.client_name,
                'status': estimate.status,
                'total_value': float(estimate.total_with_tax),
                'estimate_date': estimate.estimate_date.isoformat(),
                'approved_date': estimate.updated_at.isoformat(),
            })
        
        # ========== PERFORMANCE METRICS ==========
        approval_rate = (approved_count / total_estimates * 100) if total_estimates > 0 else 0
        rejection_rate = (rejected_count / total_estimates * 100) if total_estimates > 0 else 0
        pending_rate = (pending_count / total_estimates * 100) if total_estimates > 0 else 0
        average_value = total_value / total_estimates if total_estimates > 0 else 0
        
        # ========== COMPILE RESPONSE ==========
        dashboard_data = {
            'overview': {
                'total_estimates': total_estimates,
                'pending': pending_count,
                'sent': sent_count,
                'approved': approved_count,
                'rejected': rejected_count,
            },
            'value_summary': {
                'pending_value': round(pending_value, 2),
                'sent_value': round(sent_value, 2),
                'approved_value': round(approved_value, 2),
                'rejected_value': round(rejected_value, 2),
                'total_value': round(total_value, 2),
            },
            'due_soon': due_soon_data,
            'recent_estimates': recent_data,
            'completed_estimates': completed_data,
            'performance': {
                'approval_rate': round(approval_rate, 2),
                'rejection_rate': round(rejection_rate, 2),
                'pending_rate': round(pending_rate, 2),
                'average_estimate_value': round(average_value, 2),
            },
        }
        
        return Response(
            format_response(
                success=True,
                message="Estimator dashboard retrieved successfully",
                data=dashboard_data
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving dashboard: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
