from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Collection, EndpointResponse, MockEndpoint


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CollectionSerializer(serializers.ModelSerializer):
    endpoint_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
            "endpoint_count",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_endpoint_count(self, obj):
        return obj.endpoints.count()


class EndpointResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndpointResponse
        fields = [
            "id",
            "endpoint",
            "name",
            "description",
            "response_status",
            "content_type",
            "response_body",
            "custom_headers",
            "is_default",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MockEndpointSerializer(serializers.ModelSerializer):
    collection_slug = serializers.CharField(source="collection.slug", read_only=True)
    full_path = serializers.SerializerMethodField()
    responses = EndpointResponseSerializer(many=True, read_only=True)

    class Meta:
        model = MockEndpoint
        fields = [
            "id",
            "collection",
            "collection_slug",
            "display_name",
            "description",
            "path",
            "http_method",
            "response_status",
            "content_type",
            "content_encoding",
            "response_body",
            "custom_headers",
            "enable_dynamic_response",
            "enable_request_logger",
            "response_delay",
            "position",
            "is_active",
            "created_at",
            "updated_at",
            "full_path",
            "responses",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_full_path(self, obj):
        return obj.get_full_path()


class MockEndpointDetailSerializer(MockEndpointSerializer):
    collection_name = serializers.CharField(source="collection.name", read_only=True)

    class Meta(MockEndpointSerializer.Meta):
        fields = MockEndpointSerializer.Meta.fields + ["collection_name"]
