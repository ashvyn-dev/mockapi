"""Models for Domains."""

import json

from django.db import models


class Collection(models.Model):
    """
    Represents a collection/project.

    Each collection is accessed via /{slug}/
    """

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-safe collection identifier (e.g., 'myproject' becomes /myproject/)",
    )
    name = models.CharField(
        max_length=200, help_text="Display name for this collection"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collections",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class."""

        ordering = ["slug"]
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

    def __str__(self):
        """Give string representation."""
        return f"{self.slug} - {self.name}"


class MockEndpoint(models.Model):
    """
    Individual API endpoints within a collection.

    URL structure: /{collection.slug}/{endpoint.path}
    """

    HTTP_METHODS = [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("PATCH", "PATCH"),
        ("DELETE", "DELETE"),
        ("OPTIONS", "OPTIONS"),
    ]

    HTTP_STATUS_CODES = [
        (200, "200 - OK"),
        (201, "201 - Created"),
        (202, "202 - Accepted"),
        (204, "204 - No Content"),
        (400, "400 - Bad Request"),
        (401, "401 - Unauthorized"),
        (403, "403 - Forbidden"),
        (404, "404 - Not Found"),
        (405, "405 - Method Not Allowed"),
        (409, "409 - Conflict"),
        (422, "422 - Unprocessable Entity"),
        (429, "429 - Too Many Requests"),
        (500, "500 - Internal Server Error"),
        (502, "502 - Bad Gateway"),
        (503, "503 - Service Unavailable"),
        (504, "504 - Gateway Timeout"),
    ]

    CONTENT_TYPES = [
        ("application/json", "application/json"),
        ("application/xml", "application/xml"),
        ("text/plain", "text/plain"),
        ("text/html", "text/html"),
        ("application/x-www-form-urlencoded", "application/x-www-form-urlencoded"),
    ]

    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="endpoints"
    )
    display_name = models.CharField(
        max_length=255, help_text="Display name for this endpoint"
    )
    description = models.TextField(blank=True)

    # Request Configuration
    path = models.CharField(
        max_length=500,
        help_text="Path after collection (e.g., 'users' becomes /{collection}/users)",
    )
    http_method = models.CharField(max_length=10, choices=HTTP_METHODS, default="GET")

    # Response Configuration
    response_status = models.IntegerField(choices=HTTP_STATUS_CODES, default=200)
    content_type = models.CharField(
        max_length=100, choices=CONTENT_TYPES, default="application/json"
    )
    content_encoding = models.CharField(
        max_length=50, blank=True, help_text="Content-Encoding header"
    )
    response_body = models.TextField(
        default='{"msg": "Hello World"}',
        help_text="Response body (JSON, XML, text, etc.)",
    )

    # Additional Headers (stored as JSON)
    custom_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom headers as key-value pairs (e.g., {'X-Custom-Header': 'value'})",
    )

    # Features
    enable_dynamic_response = models.BooleanField(
        default=False, help_text="Enable dynamic templating (future feature)"
    )
    enable_request_logger = models.BooleanField(
        default=True, help_text="Log requests to this endpoint"
    )
    response_delay = models.IntegerField(
        default=0, help_text="Response delay in seconds"
    )

    # Metadata
    position = models.IntegerField(default=0, help_text="Order position in collection")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta Class."""

        ordering = ["position", "path"]
        verbose_name = "Mock Endpoint"
        verbose_name_plural = "Mock Endpoints"
        unique_together = ["collection", "path", "http_method"]

    def __str__(self):
        """Give string representation."""
        return f"{self.http_method} /{self.collection.slug}/{self.path}"

    def get_full_path(self):
        """Get the full path for this endpoint."""
        path = self.path.strip("/")
        return (
            f"/{self.collection.slug}/{path}" if path else f"/{self.collection.slug}/"
        )

    def get_response_headers(self):
        """Get all response headers including custom ones."""
        headers = {
            "Content-Type": self.content_type,
        }
        if self.content_encoding:
            headers["Content-Encoding"] = self.content_encoding

        # Add custom headers
        if self.custom_headers:
            headers.update(self.custom_headers)

        return headers


class EndpointResponse(models.Model):
    """
    Multiple responses for an endpoint.

    Can be used for different scenarios (success, error, etc.)
    """

    endpoint = models.ForeignKey(
        MockEndpoint, on_delete=models.CASCADE, related_name="responses"
    )
    name = models.CharField(
        max_length=200, help_text="Response name (e.g., Success, Error)"
    )
    description = models.TextField(blank=True)

    # Response Configuration
    response_status = models.IntegerField(
        choices=MockEndpoint.HTTP_STATUS_CODES, default=200
    )
    content_type = models.CharField(
        max_length=100, choices=MockEndpoint.CONTENT_TYPES, default="application/json"
    )
    response_body = models.TextField(
        default='{"message": "Success"}', help_text="Response body"
    )
    custom_headers = models.JSONField(
        default=dict, blank=True, help_text="Custom headers for this response"
    )

    # Metadata
    is_default = models.BooleanField(
        default=False, help_text="Use this as the default response"
    )
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class."""

        ordering = ["position", "created_at"]
        verbose_name = "Endpoint Response"
        verbose_name_plural = "Endpoint Responses"

    def __str__(self):
        """Give string representation."""
        return f"{self.endpoint.display_name} - {self.name} ({self.response_status})"
