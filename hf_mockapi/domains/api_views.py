from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import Collection, MockEndpoint, EndpointResponse
from django.contrib.auth.models import User
from .serializers import (
    CollectionSerializer,
    MockEndpointSerializer,
    MockEndpointDetailSerializer,
    EndpointResponseSerializer,
    UserSerializer,
)


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Collection.objects.filter(is_active=True)
        return queryset.order_by("slug")

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
