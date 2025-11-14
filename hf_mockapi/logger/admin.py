from django.contrib import admin
from django.utils.html import format_html

from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "method",
        "short_path",
        "response_status",
        "response_time_ms",
        "ip_address",
        "endpoint_link",
    )
    list_filter = ("method", "response_status", "timestamp")
    search_fields = ("path", "ip_address", "user_agent")
    readonly_fields = (
        "endpoint",
        "method",
        "path",
        "query_params",
        "request_headers",
        "request_body",
        "response_status",
        "response_headers",
        "response_body",
        "ip_address",
        "user_agent",
        "timestamp",
        "response_time_ms",
    )

    fieldsets = (
        (
            "Request Information",
            {
                "fields": (
                    "endpoint",
                    "method",
                    "path",
                    "query_params",
                    "request_headers",
                    "request_body",
                )
            },
        ),
        (
            "Response Information",
            {
                "fields": (
                    "response_status",
                    "response_headers",
                    "response_body",
                    "response_time_ms",
                )
            },
        ),
        ("Client Information", {"fields": ("ip_address", "user_agent", "timestamp")}),
    )

    def short_path(self, obj):
        return obj.path[:50] + "..." if len(obj.path) > 50 else obj.path

    short_path.short_description = "Path"

    def endpoint_link(self, obj):
        if obj.endpoint:
            url = f"/admin/domains/mockendpoint/{obj.endpoint.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.endpoint)
        return "-"

    endpoint_link.short_description = "Endpoint"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
