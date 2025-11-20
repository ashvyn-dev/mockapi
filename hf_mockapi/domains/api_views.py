from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Collection, EndpointResponse, MockEndpoint
from .openapi_utils import (generate_openapi_schema, import_openapi_schema,
                            validate_openapi_schema)
from .serializers import (CollectionSerializer, EndpointResponseSerializer,
                          MockEndpointDetailSerializer, MockEndpointSerializer,
                          UserSerializer)


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Collection.objects.filter(is_active=True)
        return queryset.order_by("slug")

    def get_object(self):
        slug = self.kwargs.get(self.lookup_field)
        obj = get_object_or_404(Collection, slug=slug, is_active=True)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def endpoints(self, request, slug=None):
        collection = self.get_object()
        endpoints = collection.endpoints.filter(is_active=True).order_by(
            "position", "path"
        )
        serializer = MockEndpointSerializer(endpoints, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="openapi-schema")
    def openapi_schema(self, request, slug=None):
        """Get OpenAPI schema for this collection."""
        try:
            collection = self.get_object()
            schema = generate_openapi_schema(collection)

            format_type = request.query_params.get("format", "download")

            if format_type == "json":
                import json

                import yaml

                schema_dict = yaml.safe_load(schema)
                return Response(schema_dict)
            elif format_type == "yaml":
                return Response(schema, content_type="text/plain")
            else:
                response = HttpResponse(schema, content_type="application/x-yaml")
                response["Content-Disposition"] = (
                    f'attachment; filename="{collection.slug}-openapi.yaml"'
                )
                return response
        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="import-openapi")
    def import_openapi(self, request, slug=None):
        """Import OpenAPI schema to update collection and endpoints."""
        collection = self.get_object()
        yaml_content = request.data.get("schema")

        if not yaml_content:
            return Response(
                {"error": "Schema content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = import_openapi_schema(collection, yaml_content)

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put"], url_path="update-openapi")
    def update_openapi(self, request, slug=None):
        """Update the custom OpenAPI schema for this collection."""
        collection = self.get_object()
        yaml_content = request.data.get("schema")

        if not yaml_content:
            return Response(
                {"error": "Schema content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid, error = validate_openapi_schema(yaml_content)
        if not is_valid:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        collection.openapi_schema = yaml_content
        collection.save()

        return Response({"message": "OpenAPI schema updated successfully"})

    @action(detail=True, methods=["delete"], url_path="reset-openapi")
    def reset_openapi(self, request, slug=None):
        """Reset custom OpenAPI schema (will auto-generate from endpoints)."""
        collection = self.get_object()
        collection.openapi_schema = ""
        collection.save()

        return Response({"message": "OpenAPI schema reset successfully"})


class MockEndpointViewSet(viewsets.ModelViewSet):
    queryset = MockEndpoint.objects.all()
    serializer_class = MockEndpointDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MockEndpoint.objects.filter(is_active=True)
        collection_slug = self.request.query_params.get("collection", None)

        if collection_slug:
            queryset = queryset.filter(collection__slug=collection_slug)

        return (
            queryset.select_related("collection")
            .prefetch_related("responses")
            .order_by("position", "path")
        )


class EndpointResponseViewSet(viewsets.ModelViewSet):
    queryset = EndpointResponse.objects.all()
    serializer_class = EndpointResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EndpointResponse.objects.all()
        endpoint_id = self.request.query_params.get("endpoint", None)

        if endpoint_id:
            queryset = queryset.filter(endpoint_id=endpoint_id)

        return queryset.order_by("position", "name")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(username=username, email=email, password=password)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
