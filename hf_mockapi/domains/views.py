from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import time

from .models import Collection, MockEndpoint
from logger.models import RequestLog


@csrf_exempt
def mock_api_handler(request, collection_slug, endpoint_path=""):
    """
    Main handler for all mock API requests
    URL structure: /{collection_slug}/{endpoint_path}
    """
    start_time = time.time()

    # Find the collection
    collection = get_object_or_404(Collection, slug=collection_slug, is_active=True)

    # Normalize endpoint path
    endpoint_path = endpoint_path.strip("/")

    # Find matching endpoint
    try:
        endpoint = MockEndpoint.objects.get(
            collection=collection,
            path=endpoint_path,
            http_method=request.method,
            is_active=True,
        )
    except MockEndpoint.DoesNotExist:
        error_message = {
            "error": "Endpoint not found",
            "details": f"No mock found for {request.method} /{collection_slug}/{endpoint_path}",
        }
        return JsonResponse(error_message, status=404)

    # Apply response delay if configured
    if endpoint.response_delay > 0:
        time.sleep(endpoint.response_delay)

    # Check for alternative responses (use default if exists, otherwise use endpoint's default)
    response_to_use = None
    default_response = endpoint.responses.filter(is_default=True).first()

    if default_response:
        # Use the marked default response
        response_status = default_response.response_status
        content_type = default_response.content_type
        response_body = default_response.response_body
        custom_headers = default_response.custom_headers or {}
    else:
        # Use endpoint's built-in default response
        response_status = endpoint.response_status
        content_type = endpoint.content_type
        response_body = endpoint.response_body
        custom_headers = endpoint.custom_headers or {}

    # Prepare response headers
    response_headers = {"Content-Type": content_type}
    if endpoint.content_encoding:
        response_headers["Content-Encoding"] = endpoint.content_encoding

    # Add custom headers
    response_headers.update(custom_headers)

    # Parse and create response
    try:
        if content_type == "application/json":
            response_data = json.loads(response_body)
            response = JsonResponse(response_data, status=response_status, safe=False)
        else:
            response = HttpResponse(
                response_body, status=response_status, content_type=content_type
            )
    except json.JSONDecodeError:
        # If JSON parsing fails, return as-is
        response = HttpResponse(
            response_body, status=response_status, content_type=content_type
        )

    # Add custom headers to response
    for key, value in response_headers.items():
        response[key] = value

    # Log request if enabled
    if endpoint.enable_request_logger:
        response_time = int((time.time() - start_time) * 1000)  # Convert to ms

        try:
            request_body = request.body.decode("utf-8")
        except:
            request_body = ""

        RequestLog.objects.create(
            endpoint=endpoint,
            method=request.method,
            path=request.path,
            query_params=dict(request.GET),
            request_headers=dict(request.headers),
            request_body=request_body,
            response_status=response_status,
            response_headers=response_headers,
            response_body=response_body,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            response_time_ms=response_time,
        )

    return response


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@csrf_exempt
def collection_root_handler(request, collection_slug):
    """
    Handler for root collection path (e.g., /collection1/)
    Looks for an endpoint with empty path
    """
    return mock_api_handler(request, collection_slug, "")
