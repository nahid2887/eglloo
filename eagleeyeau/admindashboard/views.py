# admindashboard/views.py
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from eagleeyeau.response_formatter import format_response
from .models import Material, EstimateDefaults, Component
from .serializers import MaterialSerializer, EstimateDefaultsSerializer, ComponentSerializer


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
        tags=['Materials']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message="Materials retrieved successfully",
                    data=serializer.data
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
        tags=['Estimate Defaults']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message="Estimate defaults retrieved successfully",
                    data=serializer.data
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
        tags=['Components']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                format_response(
                    success=True,
                    message="Components retrieved successfully",
                    data=serializer.data
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
        request_body=ComponentSerializer,
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
        request_body=ComponentSerializer,
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
        request_body=ComponentSerializer,
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