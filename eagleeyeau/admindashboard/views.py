# admindashboard/views.py
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from eagleeyeau.response_formatter import format_response
from .models import Material, EstimateDefaults, Component
from .serializers import MaterialSerializer, EstimateDefaultsSerializer, ComponentSerializer
from estimator.models import Estimate
from estimator.serializers import EstimateSerializer, EstimateListSerializer, AdminEstimateListSerializer
from Project_manager.models import Project, Task
from Project_manager.serializers import ProjectListSerializer, ProjectDetailSerializer, TaskSerializer


# ====================== PERMISSIONS ======================
class IsAdmin(permissions.BasePermission):
    """Allow only Admin users"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'Admin'
        )


class IsAdminOrEstimator(permissions.BasePermission):
    """Allow Admin or Estimator users"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['Admin', 'Estimator']
        )


# ====================== MATERIAL VIEWSET ======================
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="List all materials",
        operation_description="Get all materials. Admin only.",
        responses={200: MaterialSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description='Single search box. Searches material_name, supplier, category, unit. If numeric, also matches cost_per_unit. If date (YYYY-MM-DD), matches created_at date.',
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Materials']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()

            q = request.query_params.get('q', '').strip()
            filters_applied = {'q': q if q else None}

            if q:
                # Text search across common fields
                text_q = (
                    Q(material_name__icontains=q) |
                    Q(supplier__icontains=q) |
                    Q(category__icontains=q) |
                    Q(unit__icontains=q)
                )

                or_q = text_q

                # Numeric search for cost_per_unit
                try:
                    from decimal import Decimal
                    cost_val = Decimal(q)
                    or_q = or_q | Q(cost_per_unit=cost_val)
                except Exception:
                    # not numeric
                    pass

                # Date search (YYYY-MM-DD)
                try:
                    from datetime import datetime
                    date_val = datetime.strptime(q, '%Y-%m-%d').date()
                    or_q = or_q | Q(created_at__date=date_val)
                except Exception:
                    # not a date in that format
                    pass

                queryset = queryset.filter(or_q)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message=f"Materials retrieved successfully (Total: {queryset.count()})",
                    data={
                        'total_count': queryset.count(),
                        'filters_applied': filters_applied,
                        'results': serializer.data
                    }
                ),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                format_response(
                    success=False,
                    message=f"Error retrieving materials: {str(e)}",
                    data=None
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Retrieve a material",
        operation_description="Get one material by ID. Admin only.",
        responses={200: MaterialSerializer(), 404: "Not Found"},
        tags=['Materials']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                format_response(
                    success=True,
                    message="Material retrieved successfully",
                    data=serializer.data
                ),
                status=status.HTTP_200_OK
            )
        except Material.DoesNotExist:
            return Response(
                format_response(success=False, message="Material not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Create a new material",
        operation_description="Admin only.",
        request_body=MaterialSerializer,
        responses={201: MaterialSerializer(), 400: "Bad Request"},
        tags=['Materials']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(
                    format_response(
                        success=True,
                        message="Material created successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data provided",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Update material (PUT)",
        operation_description="Full update. Admin only.",
        request_body=MaterialSerializer,
        responses={200: MaterialSerializer(), 400: "Bad Request", 404: "Not Found"},
        tags=['Materials']
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Material updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Material.DoesNotExist:
            return Response(
                format_response(success=False, message="Material not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Partially update material (PATCH)",
        operation_description="Admin only.",
        request_body=MaterialSerializer,
        responses={200: MaterialSerializer(), 400: "Bad Request", 404: "Not Found"},
        tags=['Materials']
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Material updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Material.DoesNotExist:
            return Response(
                format_response(success=False, message="Material not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete a material",
        operation_description="Admin only.",
        responses={200: "Deleted", 404: "Not Found"},
        tags=['Materials']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            material_name = instance.material_name
            instance.delete()
            return Response(
                format_response(
                    success=True,
                    message=f"Material '{material_name}' deleted successfully",
                    data=None
                ),
                status=status.HTTP_200_OK
            )
        except Material.DoesNotExist:
            return Response(
                format_response(success=False, message="Material not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================== ESTIMATE DEFAULTS VIEWSET ======================
class EstimateDefaultsViewSet(viewsets.ModelViewSet):
    queryset = EstimateDefaults.objects.all()
    serializer_class = EstimateDefaultsSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="List estimate defaults",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description='Search by name, description, or category',
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Estimate Defaults']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Get search parameter
            search_query = request.query_params.get('search', '').strip()
            
            # Apply universal search across multiple fields
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__icontains=search_query)
                )
            
            serializer = self.get_serializer(queryset, many=True)
            
            filters_applied = {
                'search': search_query if search_query else None,
            }
            
            return Response(
                format_response(
                    success=True,
                    message=f"Estimate defaults retrieved successfully (Total: {queryset.count()})",
                    data={
                        'total_count': queryset.count(),
                        'filters_applied': filters_applied,
                        'results': serializer.data
                    }
                ),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_summary="Retrieve estimate default",
        tags=['Estimate Defaults']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                format_response(
                    success=True,
                    message="Estimate default retrieved successfully",
                    data=serializer.data
                ),
                status=status.HTTP_200_OK
            )
        except EstimateDefaults.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate default not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Create estimate default",
        request_body=EstimateDefaultsSerializer,
        tags=['Estimate Defaults']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(
                    format_response(
                        success=True,
                        message="Estimate default created successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Update estimate default (PUT)",
        request_body=EstimateDefaultsSerializer,
        tags=['Estimate Defaults']
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Estimate default updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except EstimateDefaults.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate default not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Partial update estimate default (PATCH)",
        request_body=EstimateDefaultsSerializer,
        tags=['Estimate Defaults']
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Estimate default updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except EstimateDefaults.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate default not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete estimate default",
        tags=['Estimate Defaults']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            name = instance.name
            instance.delete()
            return Response(
                format_response(
                    success=True,
                    message=f"Estimate default '{name}' deleted successfully",
                    data=None
                ),
                status=status.HTTP_200_OK
            )
        except EstimateDefaults.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate default not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================== COMPONENT VIEWSET ======================
class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="List components",
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description='Search by component_name, description, or base_price',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        tags=['Components']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            q = request.query_params.get('q', '').strip()
            filters_applied = {'q': q if q else None}

            if q:
                # Text search across text fields
                text_q = (
                    Q(component_name__icontains=q) |
                    Q(description__icontains=q)
                )

                or_q = text_q

                # Numeric search for base_price
                try:
                    from decimal import Decimal
                    price_val = Decimal(q)
                    or_q = or_q | Q(base_price=price_val)
                except Exception:
                    pass

                # Date search (YYYY-MM-DD)
                try:
                    from datetime import datetime
                    date_val = datetime.strptime(q, '%Y-%m-%d').date()
                    or_q = or_q | Q(created_at__date=date_val)
                except Exception:
                    pass

                queryset = queryset.filter(or_q)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message=f"Components retrieved successfully (Total: {queryset.count()})",
                    data={
                        'total_count': queryset.count(),
                        'filters_applied': filters_applied,
                        'results': serializer.data
                    }
                ),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Retrieve component",
        tags=['Components']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                format_response(
                    success=True,
                    message="Component retrieved successfully",
                    data=serializer.data
                ),
                status=status.HTTP_200_OK
            )
        except Component.DoesNotExist:
            return Response(
                format_response(success=False, message="Component not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Create component",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['component_name', 'base_price'],
            properties={
                'component_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the component'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Component description (optional)'),
                'base_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Base price of the component'),
                'material_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Materials with quantities',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Material ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 2, 'quantity': 5}]
                ),
                'estimate_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Estimate defaults with quantities',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Estimate Default ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 7, 'quantity': 5}]
                ),
            },
            example={
                'component_name': 'Rhonda Campos',
                'description': 'Beatae culpa volupt',
                'base_price': 215,
                'material_quantities': [{'id': 2, 'quantity': 5}],
                'estimate_quantities': [{'id': 7, 'quantity': 5}],
            }
        ),
        tags=['Components']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(
                    format_response(
                        success=True,
                        message="Component created successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_201_CREATED
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Update component (PUT)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'component_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the component'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Component description'),
                'base_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Base price of the component'),
                'material_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Materials with quantities',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Material ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 2, 'quantity': 5}]
                ),
                'estimate_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Estimate defaults with quantities',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Estimate Default ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 7, 'quantity': 5}]
                ),
            },
            example={
                'component_name': 'Updated Component',
                'description': 'Updated description',
                'base_price': 250,
                'material_quantities': [{'id': 2, 'quantity': 10}],
                'estimate_quantities': [{'id': 7, 'quantity': 8}],
            }
        ),
        tags=['Components']
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Component updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Component.DoesNotExist:
            return Response(
                format_response(success=False, message="Component not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Partial update component (PATCH)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Update any fields - all fields are optional',
            properties={
                'component_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the component (optional)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Component description (optional)'),
                'base_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Base price of the component (optional)'),
                'material_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Materials with quantities - replaces existing (optional)',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Material ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 2, 'quantity': 5}]
                ),
                'estimate_quantities': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='Estimate defaults with quantities - replaces existing (optional)',
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Estimate Default ID'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity needed'),
                        }
                    ),
                    example=[{'id': 7, 'quantity': 5}]
                ),
            },
            example={
                'component_name': 'Updated Component Name',
                'material_quantities': [{'id': 2, 'quantity': 15}],
            }
        ),
        tags=['Components']
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    format_response(
                        success=True,
                        message="Component updated successfully",
                        data=serializer.data
                    ),
                    status=status.HTTP_200_OK
                )
            return Response(
                format_response(
                    success=False,
                    message="Invalid data",
                    data=serializer.errors
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Component.DoesNotExist:
            return Response(
                format_response(success=False, message="Component not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete component",
        tags=['Components']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            name = instance.component_name
            instance.delete()
            return Response(
                format_response(
                    success=True,
                    message=f"Component '{name}' deleted successfully",
                    data=None
                ),
                status=status.HTTP_200_OK
            )
        except Component.DoesNotExist:
            return Response(
                format_response(success=False, message="Component not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================== COMPREHENSIVE LIST (Admin + Estimator) ======================
@swagger_auto_schema(
    method='get',
    operation_summary="Get all materials, defaults, and components with search and filter",
    operation_description="""
    Get all materials, defaults, and components with optional search and filtering.
    
    Query Parameters:
    - search: Search across all tables (materials, estimate defaults, components)
    - table_type: Filter by table type (materials, estimate_defaults, components)
    - sort_by: Sort field (name, created_at, cost_per_unit, base_price)
    - sort_order: asc or desc (default: asc)
    
    - Admin: sees all from their company
    - Estimator: sees only admin-created items from their company
    
    Examples:
    - /api/admin/comprehensive-list/ - Get all items
    - /api/admin/comprehensive-list/?search=wood - Search for "wood" in all tables
    - /api/admin/comprehensive-list/?table_type=materials - Get only materials
    - /api/admin/comprehensive-list/?table_type=materials&sort_by=material_name&sort_order=desc
    - /api/admin/comprehensive-list/?search=oak&table_type=materials
    """,
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description='Search query', type=openapi.TYPE_STRING),
        openapi.Parameter('table_type', openapi.IN_QUERY, description='Filter by table (materials, estimate_defaults, components)', type=openapi.TYPE_STRING),
        openapi.Parameter('sort_by', openapi.IN_QUERY, description='Sort field name', type=openapi.TYPE_STRING),
        openapi.Parameter('sort_order', openapi.IN_QUERY, description='Sort order (asc or desc)', type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Data retrieved successfully",
                    "data": {
                        "materials": [],
                        "estimate_defaults": [],
                        "components": [],
                        "summary": {
                            "total_materials": 0,
                            "total_estimate_defaults": 0,
                            "total_components": 0,
                            "user_role": "Admin",
                            "company_name": "ABC Co",
                            "search_applied": False,
                            "filters_applied": {}
                        }
                    }
                }
            }
        )
    },
    tags=['Dashboard - Combined Data']
)
@api_view(['GET'])
@permission_classes([IsAdminOrEstimator])
def get_comprehensive_list(request):
    try:
        from django.db.models import Q
        
        user = request.user
        company = user.company_name
        role = user.role

        if role not in ['Admin', 'Estimator']:
            return Response(
                format_response(success=False, message="Access denied", data=None),
                status=status.HTTP_403_FORBIDDEN
            )

        # Get query parameters
        search_query = request.query_params.get('search', '').strip()
        table_type = request.query_params.get('table_type', '').strip().lower()
        sort_by = request.query_params.get('sort_by', 'name').strip()
        sort_order = request.query_params.get('sort_order', 'asc').strip().lower()
        
        # Validate sort_order
        sort_order = '' if sort_order == 'asc' else '-'
        
        # Base querysets filtered by company and creator role
        materials = Material.objects.filter(created_by__company_name=company)
        estimate_defaults = EstimateDefaults.objects.filter(created_by__company_name=company)
        components = Component.objects.filter(created_by__company_name=company)

        if role == 'Estimator':
            materials = materials.filter(created_by__role='Admin')
            estimate_defaults = estimate_defaults.filter(created_by__role='Admin')
            components = components.filter(created_by__role='Admin')

        # Apply search if provided
        search_applied = False
        if search_query:
            search_applied = True
            # Search in materials by material_name, supplier, category
            materials = materials.filter(
                Q(material_name__icontains=search_query) |
                Q(supplier__icontains=search_query) |
                Q(category__icontains=search_query)
            )
            # Search in estimate defaults by name, description, category
            estimate_defaults = estimate_defaults.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query)
            )
            # Search in components by component_name, description
            components = components.filter(
                Q(component_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply sorting
        sort_mapping = {
            'materials': {'name': 'material_name', 'created_at': 'created_at', 'cost': 'cost_per_unit'},
            'estimate_defaults': {'name': 'name', 'created_at': 'created_at', 'cost': 'cost'},
            'components': {'name': 'component_name', 'created_at': 'created_at', 'cost': 'base_price'}
        }
        
        # Sort materials
        if sort_by in sort_mapping['materials']:
            materials = materials.order_by(f'{sort_order}{sort_mapping["materials"][sort_by]}')
        else:
            materials = materials.order_by(f'{sort_order}material_name')
        
        # Sort estimate defaults
        if sort_by in sort_mapping['estimate_defaults']:
            estimate_defaults = estimate_defaults.order_by(f'{sort_order}{sort_mapping["estimate_defaults"][sort_by]}')
        else:
            estimate_defaults = estimate_defaults.order_by(f'{sort_order}name')
        
        # Sort components
        if sort_by in sort_mapping['components']:
            components = components.order_by(f'{sort_order}{sort_mapping["components"][sort_by]}')
        else:
            components = components.order_by(f'{sort_order}component_name')

        # Filter by table type if specified
        filters_applied = {}
        if table_type:
            filters_applied['table_type'] = table_type
            if table_type == 'materials':
                estimate_defaults = EstimateDefaults.objects.none()
                components = Component.objects.none()
            elif table_type == 'estimate_defaults':
                materials = Material.objects.none()
                components = Component.objects.none()
            elif table_type == 'components':
                materials = Material.objects.none()
                estimate_defaults = EstimateDefaults.objects.none()

        data = {
            "materials": MaterialSerializer(materials, many=True).data,
            "estimate_defaults": EstimateDefaultsSerializer(estimate_defaults, many=True).data,
            "components": ComponentSerializer(components, many=True).data,
            "summary": {
                "total_materials": materials.count(),
                "total_estimate_defaults": estimate_defaults.count(),
                "total_components": components.count(),
                "user_role": role,
                "company_name": company or "Not Specified",
                "search_applied": search_applied,
                "search_query": search_query if search_applied else None,
                "filters_applied": filters_applied,
                "sort_by": sort_by,
                "sort_order": 'desc' if sort_order == '-' else 'asc'
            }
        }

        return Response(
            format_response(success=True, message="Data retrieved successfully", data=data),
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            format_response(success=False, message=f"Error: {str(e)}", data=None),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ====================== ADMIN ESTIMATE MANAGEMENT VIEWSET ======================
class AdminEstimateViewSet(viewsets.ModelViewSet):
    """
    Admin dashboard for viewing and managing all estimates.
    Admins can search by client name, project name, estimate number, change status, and delete estimates.
    Returns creator name and email in list responses.
    """
    queryset = Estimate.objects.all().order_by('-created_at')
    serializer_class = AdminEstimateListSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_summary="List all estimates with search",
        operation_description="Get all estimates with search and filter capabilities. Admin only. Includes creator name and email.",
        responses={200: AdminEstimateListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description='Search by client_name, project_name, estimate_number, or serial_number',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description='Filter by status: pending, sent, approved, rejected',
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Admin - Estimates']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            # Search parameter
            q = request.query_params.get('q', '').strip()
            status_filter = request.query_params.get('status', '').strip()
            
            filters_applied = {'q': q if q else None, 'status': status_filter if status_filter else None}
            
            # Search across multiple fields
            if q:
                queryset = queryset.filter(
                    Q(client_name__icontains=q) |
                    Q(project_name__icontains=q) |
                    Q(estimate_number__icontains=q) |
                    Q(serial_number__icontains=q)
                )
            
            # Filter by status
            if status_filter and status_filter in ['pending', 'sent', 'approved', 'rejected']:
                queryset = queryset.filter(status=status_filter)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message=f"Estimates retrieved successfully (Total: {queryset.count()})",
                    data={
                        'total_count': queryset.count(),
                        'filters_applied': filters_applied,
                        'results': serializer.data
                    }
                ),
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Retrieve estimate details",
        operation_description="Get full estimate details with all items. Admin only.",
        responses={200: EstimateSerializer()},
        tags=['Admin - Estimates']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            estimate = self.get_object()
            serializer = EstimateSerializer(estimate)
            return Response(
                format_response(
                    success=True,
                    message="Estimate retrieved successfully",
                    data=serializer.data
                ),
                status=status.HTTP_200_OK
            )
        except Estimate.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Change estimate status",
        operation_description="Update estimate status. Admin only.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['pending', 'sent', 'approved', 'rejected'],
                    description='New status for the estimate'
                ),
            },
            required=['status']
        ),
        responses={200: EstimateSerializer()},
        tags=['Admin - Estimates']
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def change_status(self, request, pk=None):
        """Change the status of an estimate"""
        try:
            estimate = self.get_object()
            new_status = request.data.get('status', '').lower().strip()
            
            # Validate status
            valid_statuses = ['pending', 'sent', 'approved', 'rejected']
            if new_status not in valid_statuses:
                return Response(
                    format_response(
                        success=False,
                        message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                        data=None
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status
            old_status = estimate.status
            estimate.status = new_status
            estimate.save()
            
            serializer = EstimateSerializer(estimate)
            return Response(
                format_response(
                    success=True,
                    message=f"Estimate status updated from '{old_status}' to '{new_status}'",
                    data=serializer.data
                ),
                status=status.HTTP_200_OK
            )
        
        except Estimate.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete estimate",
        operation_description="Delete an estimate permanently. Admin only.",
        responses={
            204: openapi.Response(description="Estimate deleted successfully"),
            404: openapi.Response(description="Estimate not found"),
            500: openapi.Response(description="Server error")
        },
        tags=['Admin - Estimates']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an estimate"""
        try:
            estimate = self.get_object()
            estimate_id = estimate.id
            serial_number = estimate.serial_number
            estimate_number = estimate.estimate_number or 'N/A'
            
            # Delete the estimate
            estimate.delete()
            
            return Response(
                format_response(
                    success=True,
                    message=f"Estimate (ID: {estimate_id}, Serial: {serial_number}, Number: {estimate_number}) deleted successfully",
                    data=None
                ),
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Estimate.DoesNotExist:
            return Response(
                format_response(success=False, message="Estimate not found", data=None),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                format_response(success=False, message=f"Error: {str(e)}", data=None),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ====================== ADMIN PROJECTS MANAGEMENT ======================
@swagger_auto_schema(
    method='get',
    operation_summary="List all projects of admin's company",
    operation_description="""
    Get all projects belonging to the admin's company with search and filter options.
    
    Query Parameters:
    - search: Search by project name or client name
    - status: Filter by status (not_started, in_progress, completed, on_hold, cancelled)
    - sort_by: Sort field (project_name, client_name, creating_date, start_date, status)
    - sort_order: asc or desc (default: desc for dates)
    """,
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description='Search by project or client name', type=openapi.TYPE_STRING),
        openapi.Parameter('status', openapi.IN_QUERY, description='Filter by project status', type=openapi.TYPE_STRING),
        openapi.Parameter('sort_by', openapi.IN_QUERY, description='Sort field', type=openapi.TYPE_STRING),
        openapi.Parameter('sort_order', openapi.IN_QUERY, description='Sort order (asc or desc)', type=openapi.TYPE_STRING),
    ],
    responses={200: ProjectListSerializer(many=True)},
    tags=['Admin - Projects']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def admin_all_projects(request):
    """
    Get all projects of the admin's company with search and filtering.
    """
    try:
        user = request.user
        company_name = user.company_name
        
        # Get all projects linked to estimates created by users in the same company
        projects = Project.objects.filter(
            estimate__created_by__company_name=company_name
        ).select_related('estimate', 'created_by', 'assigned_to').distinct()
        
        # Search parameter
        search_query = request.query_params.get('search', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        sort_by = request.query_params.get('sort_by', 'creating_date').strip()
        sort_order = request.query_params.get('sort_order', 'desc').strip().lower()
        
        # Apply search
        if search_query:
            projects = projects.filter(
                Q(project_name__icontains=search_query) |
                Q(client_name__icontains=search_query)
            )
        
        # Apply status filter
        valid_statuses = ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled']
        if status_filter and status_filter in valid_statuses:
            projects = projects.filter(status=status_filter)
        
        # Apply sorting
        sort_mapping = {
            'project_name': 'project_name',
            'client_name': 'client_name',
            'creating_date': 'creating_date',
            'start_date': 'start_date',
            'status': 'status',
        }
        
        sort_field = sort_mapping.get(sort_by, 'creating_date')
        sort_prefix = '' if sort_order == 'asc' else '-'
        projects = projects.order_by(f'{sort_prefix}{sort_field}')
        
        filters_applied = {
            'search': search_query if search_query else None,
            'status': status_filter if status_filter else None,
            'sort_by': sort_by,
            'sort_order': sort_order,
        }
        
        serializer = ProjectListSerializer(projects, many=True)
        
        return Response(
            format_response(
                success=True,
                message=f"Projects retrieved successfully (Total: {projects.count()})",
                data={
                    'total_count': projects.count(),
                    'filters_applied': filters_applied,
                    'results': serializer.data
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


# ====================== ADMIN PROJECT DETAILS ======================
@swagger_auto_schema(
    method='get',
    operation_summary="Get detailed view of a specific project",
    operation_description="""
    Get comprehensive project details including:
    - Project information (name, client, status, dates, amounts)
    - Estimate details (budget breakdown)
    - All tasks associated with the project
    - Project creator and assigned manager information
    - Status distribution of tasks
    
    Only accessible to admins from the same company.
    """,
    responses={
        200: openapi.Response(
            description="Project details retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'project': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'estimate': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'tasks': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'task_summary': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'by_status': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'by_priority': openapi.Schema(type=openapi.TYPE_OBJECT),
                        }
                    )
                }
            )
        ),
        404: openapi.Response(description="Project not found or access denied"),
    },
    tags=['Admin - Projects']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def admin_project_detail(request, project_id):
    """
    Get detailed information about a specific project including all tasks.
    """
    try:
        user = request.user
        company_name = user.company_name
        
        # Get the project and verify it belongs to the admin's company
        try:
            project = Project.objects.get(
                id=project_id,
                estimate__created_by__company_name=company_name
            )
        except Project.DoesNotExist:
            return Response(
                format_response(
                    success=False,
                    message="Project not found or access denied",
                    data=None
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get related tasks
        tasks = Task.objects.filter(project=project).select_related('project').prefetch_related('assigned_employees')
        
        # Calculate task summary
        task_summary = {
            'total_tasks': tasks.count(),
            'by_status': {},
            'by_priority': {},
        }
        
        # Count by status
        for status_choice in ['not_started', 'in_progress', 'completed', 'blocked']:
            count = tasks.filter(status=status_choice).count()
            task_summary['by_status'][status_choice] = count
        
        # Count by priority
        for priority_choice in ['low', 'medium', 'high']:
            count = tasks.filter(priority=priority_choice).count()
            task_summary['by_priority'][priority_choice] = count
        
        # Serialize data
        project_serializer = ProjectDetailSerializer(project)
        estimate_serializer = EstimateSerializer(project.estimate)
        tasks_serializer = TaskSerializer(tasks, many=True)
        
        data = {
            'project': project_serializer.data,
            'estimate': estimate_serializer.data,
            'tasks': tasks_serializer.data,
            'task_summary': task_summary,
        }
        
        return Response(
            format_response(
                success=True,
                message="Project details retrieved successfully",
                data=data
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


# ====================== ADMIN DASHBOARD OVERVIEW ======================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
@swagger_auto_schema(
    operation_summary="Admin Dashboard Overview",
    operation_description="""
    Comprehensive admin dashboard showing:
    - Total projects, pending requests, completed projects
    - Revenue overview (completed project revenue) - Monthly and Yearly breakdown
    - User growth analytics
    - Key metrics and statistics
    
    The revenue is calculated from the total_amount of completed projects.
    """,
    responses={
        200: openapi.Response(
            description="Admin dashboard data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'overview_stats': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'total_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                                    'pending_requests': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                    'completed_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                    'total_revenue': openapi.Schema(type=openapi.TYPE_STRING, example='$85,000.00'),
                                }
                            ),
                            'revenue_overview': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'monthly': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'month': openapi.Schema(type=openapi.TYPE_STRING, example='JAN'),
                                                'revenue': openapi.Schema(type=openapi.TYPE_NUMBER, example=5000),
                                            }
                                        )
                                    ),
                                    'yearly': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'current_year': openapi.Schema(type=openapi.TYPE_NUMBER, example=85000),
                                            'last_year': openapi.Schema(type=openapi.TYPE_NUMBER, example=72000),
                                            'growth_percentage': openapi.Schema(type=openapi.TYPE_NUMBER, example=18.06),
                                        }
                                    ),
                                }
                            ),
                            'user_growth': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'monthly': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'month': openapi.Schema(type=openapi.TYPE_STRING, example='JAN'),
                                                'count': openapi.Schema(type=openapi.TYPE_INTEGER, example=150),
                                            }
                                        )
                                    ),
                                    'total_users': openapi.Schema(type=openapi.TYPE_INTEGER, example=450),
                                    'active_users': openapi.Schema(type=openapi.TYPE_INTEGER, example=380),
                                    'monthly_growth_rate': openapi.Schema(type=openapi.TYPE_NUMBER, example=8.5),
                                }
                            ),
                            'project_stats': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'active_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                    'on_hold_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                    'cancelled_projects': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                    'average_project_value': openapi.Schema(type=openapi.TYPE_STRING, example='$17,000.00'),
                                }
                            ),
                        }
                    )
                }
            )
        ),
    },
    tags=['Admin - Dashboard']
)
def admin_dashboard_overview(request):
    """
    Get comprehensive admin dashboard with revenue and user growth analytics.
    """
    try:
        from datetime import datetime, timedelta
        from Project_manager.models import Project
        from authentication.models import User
        from decimal import Decimal
        
        today = datetime.now().date()
        current_year = today.year
        last_year = current_year - 1
        
        # ========== OVERVIEW STATS ==========
        all_projects = Project.objects.all()
        total_projects = all_projects.count()
        completed_projects = all_projects.filter(status='completed').count()
        pending_projects = all_projects.filter(status='not_started').count()
        
        # ========== REVENUE CALCULATION ==========
        # Revenue from completed projects
        completed_project_revenue = Decimal('0')
        for project in all_projects.filter(status='completed'):
            if project.total_amount:
                completed_project_revenue += project.total_amount
        
        total_revenue_str = f"${completed_project_revenue:,.2f}"
        
        # ========== MONTHLY REVENUE ==========
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        monthly_revenue_current = [0] * 12
        monthly_revenue_last_year = [0] * 12
        
        # Current year revenue by month
        for project in all_projects.filter(status='completed', updated_at__year=current_year):
            month_index = project.updated_at.month - 1
            if project.total_amount:
                monthly_revenue_current[month_index] += float(project.total_amount)
        
        # Last year revenue by month
        for project in all_projects.filter(status='completed', updated_at__year=last_year):
            month_index = project.updated_at.month - 1
            if project.total_amount:
                monthly_revenue_last_year[month_index] += float(project.total_amount)
        
        # Build monthly revenue list
        monthly_revenue = []
        for i, month in enumerate(months):
            monthly_revenue.append({
                'month': month,
                'revenue': monthly_revenue_current[i]
            })
        
        # ========== YEARLY REVENUE ==========
        current_year_total = sum(monthly_revenue_current)
        last_year_total = sum(monthly_revenue_last_year)
        
        if last_year_total > 0:
            growth_percentage = ((current_year_total - last_year_total) / last_year_total) * 100
        else:
            growth_percentage = 0 if current_year_total == 0 else 100
        
        yearly_revenue = {
            'current_year': current_year_total,
            'last_year': last_year_total,
            'growth_percentage': round(growth_percentage, 2)
        }
        
        # ========== USER GROWTH ==========
        all_users = User.objects.all()
        total_users = all_users.count()
        active_users = all_users.filter(is_active=True).count()
        
        # Monthly user count
        monthly_users = []
        for i, month in enumerate(months):
            month_num = i + 1
            # Count users created up to end of current month
            users_created = User.objects.filter(
                date_joined__year=current_year,
                date_joined__month__lte=month_num
            ).count()
            monthly_users.append({
                'month': month,
                'count': users_created
            })
        
        # Calculate monthly growth rate (average)
        if len(monthly_users) > 1:
            last_month_count = monthly_users[-1]['count']
            prev_month_count = monthly_users[-2]['count'] if len(monthly_users) > 1 else 0
            
            if prev_month_count > 0:
                monthly_growth_rate = ((last_month_count - prev_month_count) / prev_month_count) * 100
            else:
                monthly_growth_rate = 0 if last_month_count == 0 else 100
        else:
            monthly_growth_rate = 0
        
        user_growth = {
            'monthly': monthly_users,
            'total_users': total_users,
            'active_users': active_users,
            'monthly_growth_rate': round(monthly_growth_rate, 2)
        }
        
        # ========== PROJECT STATS ==========
        active_projects = all_projects.filter(status='in_progress').count()
        on_hold_projects = all_projects.filter(status='on_hold').count()
        cancelled_projects = all_projects.filter(status='cancelled').count()
        
        if completed_projects > 0:
            average_project_value = completed_project_revenue / completed_projects
            average_project_value_str = f"${average_project_value:,.2f}"
        else:
            average_project_value_str = "$0.00"
        
        project_stats = {
            'active_projects': active_projects,
            'on_hold_projects': on_hold_projects,
            'cancelled_projects': cancelled_projects,
            'average_project_value': average_project_value_str,
        }
        
        # ========== COMPILE RESPONSE ==========
        dashboard_data = {
            'overview_stats': {
                'total_projects': total_projects,
                'pending_requests': pending_projects,
                'completed_projects': completed_projects,
                'total_revenue': total_revenue_str,
            },
            'revenue_overview': {
                'monthly': monthly_revenue,
                'yearly': yearly_revenue,
            },
            'user_growth': user_growth,
            'project_stats': project_stats,
        }
        
        return Response(
            format_response(
                success=True,
                message="Admin dashboard overview retrieved successfully",
                data=dashboard_data
            ),
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            format_response(
                success=False,
                message=f"Error retrieving admin dashboard: {str(e)}",
                data=None
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )