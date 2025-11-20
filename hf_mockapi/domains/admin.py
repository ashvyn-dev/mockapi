import nested_admin
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Collection, EndpointResponse, MockEndpoint


class EndpointResponseInline(nested_admin.NestedTabularInline):
    model = EndpointResponse
    extra = 0
    fields = ("name", "response_status", "content_type", "is_default", "position")
    ordering = ["position", "name"]


class MockEndpointInline(nested_admin.NestedTabularInline):
    model = MockEndpoint
    extra = 0
    fields = (
        "display_name",
        "http_method",
        "path",
        "response_status",
        "content_type",
        "is_active",
        "position",
    )
    ordering = ["position", "path"]
    inlines = [EndpointResponseInline]


@admin.register(Collection)
class CollectionAdmin(nested_admin.NestedModelAdmin):
    list_display = ("slug_link", "name", "endpoint_count", "is_active", "openapi_status", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("slug", "name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MockEndpointInline]

    fieldsets = (
        ("Collection Information", {"fields": ("slug", "name", "description")}),
        ("OpenAPI Schema", {
            "fields": ("openapi_schema_display", "openapi_actions"),
            "classes": ("collapse",),
            "description": "View or manage the OpenAPI schema for this collection"
        }),
        ("Settings", {"fields": ("is_active", "created_by")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at", "openapi_schema_display", "openapi_actions")

    def slug_link(self, obj):
        url = reverse("admin:domains_collection_change", args=[obj.pk])
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>', url, obj.slug
        )

    slug_link.short_description = "Collection Slug"
    slug_link.admin_order_field = "slug"

    def endpoint_count(self, obj):
        count = obj.endpoints.count()
        if count > 0:
            url = (
                reverse("admin:domains_mockendpoint_changelist")
                + f"?collection__id__exact={obj.id}"
            )
            return format_html('<a href="{}">{} endpoints</a>', url, count)
        return "0 endpoints"

    endpoint_count.short_description = "Endpoints"

    def openapi_status(self, obj):
        """Display OpenAPI schema status."""
        if obj.openapi_schema:
            return format_html(
                '<span style="color: #28a745;">✓ Custom Schema</span>'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">Auto-generated</span>'
            )
    
    openapi_status.short_description = "OpenAPI Status"

    def openapi_schema_display(self, obj):
        """Display OpenAPI schema in a readonly textarea."""
        if not obj.pk:
            return "Save the collection first to view OpenAPI schema."
        from .openapi_utils import generate_openapi_schema
        try:
            schema = generate_openapi_schema(obj)
            return mark_safe(f'<textarea rows="20" cols="100" readonly style="width:100%;">{schema}</textarea>')
        except Exception as e:
            return f"Error: {e}"
    openapi_schema_display.short_description = "OpenAPI Schema (readonly)"

    def openapi_actions(self, obj):
        """Display API method info for OpenAPI schema management."""
        if not obj.pk:
            return "Save the collection first."
        api_url = f"/api/collections/{obj.slug}/openapi-schema/"
        download_url = f"/api/collections/{obj.slug}/openapi-schema/?format=yaml"
        import_url = f"/api/collections/{obj.slug}/import-openapi/"
        update_url = f"/api/collections/{obj.slug}/update-openapi/"
        reset_url = f"/api/collections/{obj.slug}/reset-openapi/"
        return mark_safe(
            f'<div>'
            f'<b>GET</b> {api_url} <br>'
            f'<b>GET</b> {download_url} <br>'
            f'<b>POST</b> {import_url} <br>'
            f'<b>PUT</b> {update_url} <br>'
            f'<b>DELETE</b> {reset_url} <br>'
            f'</div>'
        )
    openapi_actions.short_description = "OpenAPI API Methods"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(endpoints_count=Count("endpoints"))


@admin.register(MockEndpoint)
class MockEndpointAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "display_name",
        "http_method",
        "path",
        "collection_link",
        "response_status",
        "is_active",
        "test_url",
    )
    list_filter = ("http_method", "response_status", "is_active", "collection")
    search_fields = (
        "display_name",
        "path",
        "description",
        "collection__name",
        "collection__slug",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_full_path",
        "test_endpoint_link",
    )
    list_select_related = ("collection",)
    inlines = [EndpointResponseInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("collection", "display_name", "description", "position")},
        ),
        (
            "Request Configuration",
            {"fields": ("path", "http_method", "get_full_path", "test_endpoint_link")},
        ),
        (
            "Default Response Configuration",
            {
                "fields": (
                    "response_status",
                    "content_type",
                    "content_encoding",
                    "response_body",
                    "custom_headers",
                ),
                "description": "Default response (can add more responses below)",
            },
        ),
        (
            "Features",
            {
                "fields": (
                    "enable_dynamic_response",
                    "enable_request_logger",
                    "response_delay",
                )
            },
        ),
        ("Settings", {"fields": ("is_active",)}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def collection_link(self, obj):
        url = reverse("admin:domains_collection_change", args=[obj.collection.pk])
        return format_html('<a href="{}">{}</a>', url, obj.collection.slug)

    collection_link.short_description = "Collection"
    collection_link.admin_order_field = "collection__slug"

    def test_url(self, obj):
        path = obj.get_full_path()
        return format_html(
            '<a href="{}" target="_blank" style="color: #417690;">🔗 Test</a>', path
        )

    test_url.short_description = "Test"

    def get_full_path(self, obj):
        return obj.get_full_path()

    get_full_path.short_description = "Full URL Path"

    def test_endpoint_link(self, obj):
        path = obj.get_full_path()
        return format_html(
            '<a href="{}" target="_blank" style="font-size: 14px; padding: 8px 12px; '
            "background: #417690; color: white; text-decoration: none; "
            'border-radius: 4px; display: inline-block;">Open in Browser</a>',
            path,
        )

    test_endpoint_link.short_description = "Test This Endpoint"


@admin.register(EndpointResponse)
class EndpointResponseAdmin(admin.ModelAdmin):
    list_display = ("name", "endpoint", "response_status", "is_default", "position")
    list_filter = ("response_status", "is_default", "endpoint__collection")
    search_fields = ("name", "description", "endpoint__display_name")
    readonly_fields = ("created_at", "updated_at")
