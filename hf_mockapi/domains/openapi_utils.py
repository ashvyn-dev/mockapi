"""Utilities for OpenAPI schema generation and parsing."""

from typing import Any, Dict

import yaml


def generate_openapi_schema(collection) -> str:
    """
    Generate OpenAPI 3.0 YAML schema from a collection and its endpoints.

    Args:
        collection: Collection model instance

    Returns:
        YAML string representing the OpenAPI schema
    """
    # If custom schema exists, return it
    if collection.openapi_schema:
        return collection.openapi_schema

    # Generate schema from endpoints
    schema = {
        "openapi": "3.0.3",
        "info": {
            "title": collection.name,
            "description": collection.description or f"API for {collection.name}",
            "version": "1.0.0",
        },
        "servers": [
            {"url": f"/api/{collection.slug}", "description": "Mock API Server"}
        ],
        "paths": {},
    }

    # Group endpoints by path
    endpoints = collection.endpoints.filter(is_active=True).order_by(
        "path", "http_method"
    )

    for endpoint in endpoints:
        path = f"/{endpoint.path}" if endpoint.path else "/"

        if path not in schema["paths"]:
            schema["paths"][path] = {}

        # Add method to path
        method = endpoint.http_method.lower()

        operation = {
            "summary": endpoint.display_name,
            "description": endpoint.description
            or f"{endpoint.http_method} {endpoint.display_name}",
            "responses": {},
        }

        # Add default response from endpoint
        operation["responses"][str(endpoint.response_status)] = {
            "description": f"Response with status {endpoint.response_status}",
            "content": {
                endpoint.content_type: {
                    "example": _parse_response_body(
                        endpoint.response_body, endpoint.content_type
                    )
                }
            },
        }

        # Add additional responses
        for response in endpoint.responses.all():
            operation["responses"][str(response.response_status)] = {
                "description": response.description or response.name,
                "content": {
                    response.content_type: {
                        "example": _parse_response_body(
                            response.response_body, response.content_type
                        )
                    }
                },
            }

        # Add custom headers if any
        if endpoint.custom_headers:
            if str(endpoint.response_status) in operation["responses"]:
                operation["responses"][str(endpoint.response_status)]["headers"] = {
                    key: {"schema": {"type": "string"}, "example": value}
                    for key, value in endpoint.custom_headers.items()
                }

        schema["paths"][path][method] = operation

    return yaml.dump(schema, default_flow_style=False, sort_keys=False)


def _parse_response_body(body: str, content_type: str) -> Any:
    """Parse response body based on content type."""
    import json

    if content_type == "application/json":
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body
    return body


def validate_openapi_schema(yaml_content: str) -> tuple[bool, str]:
    """
    Validate OpenAPI YAML schema.

    Args:
        yaml_content: YAML string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        schema = yaml.safe_load(yaml_content)

        if not isinstance(schema, dict):
            return False, "Schema must be a valid YAML object"

        # Check for required OpenAPI fields
        if "openapi" not in schema:
            return False, "Missing required field: openapi"

        if "info" not in schema:
            return False, "Missing required field: info"

        if "paths" not in schema:
            return False, "Missing required field: paths"

        return True, ""

    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def import_openapi_schema(collection, yaml_content: str) -> tuple[bool, str]:
    """
    Import OpenAPI schema and create/update endpoints.

    Args:
        collection: Collection model instance
        yaml_content: OpenAPI YAML content

    Returns:
        Tuple of (success, message)
    """
    from .models import MockEndpoint

    try:
        schema = yaml.safe_load(yaml_content)

        # Validate schema
        is_valid, error = validate_openapi_schema(yaml_content)
        if not is_valid:
            return False, error

        # Update collection info if provided
        if "info" in schema:
            info = schema["info"]
            if "title" in info and info["title"] != collection.name:
                collection.name = info["title"]
            if "description" in info:
                collection.description = info["description"]

        # Store the custom schema
        collection.openapi_schema = yaml_content
        collection.save()

        # Import endpoints from paths
        created_count = 0
        updated_count = 0

        if "paths" in schema:
            for path, methods in schema["paths"].items():
                # Clean up path
                path = path.strip("/")

                for method, operation in methods.items():
                    if method.upper() not in dict(MockEndpoint.HTTP_METHODS):
                        continue

                    # Get or create endpoint
                    endpoint, created = MockEndpoint.objects.get_or_create(
                        collection=collection,
                        path=path,
                        http_method=method.upper(),
                        defaults={
                            "display_name": operation.get(
                                "summary", f"{method.upper()} {path}"
                            ),
                            "description": operation.get("description", ""),
                        },
                    )

                    if created:
                        created_count += 1
                    else:
                        # Update existing endpoint
                        endpoint.display_name = operation.get(
                            "summary", endpoint.display_name
                        )
                        endpoint.description = operation.get(
                            "description", endpoint.description
                        )
                        updated_count += 1

                    # Get response info from first response
                    if "responses" in operation:
                        for status_code, response_data in operation[
                            "responses"
                        ].items():
                            try:
                                status = int(status_code)
                                endpoint.response_status = status

                                # Get content type and body
                                if "content" in response_data:
                                    for content_type, content_data in response_data[
                                        "content"
                                    ].items():
                                        endpoint.content_type = content_type
                                        if "example" in content_data:
                                            import json

                                            if content_type == "application/json":
                                                endpoint.response_body = json.dumps(
                                                    content_data["example"], indent=2
                                                )
                                            else:
                                                endpoint.response_body = str(
                                                    content_data["example"]
                                                )
                                        break
                                break
                            except (ValueError, KeyError):
                                continue

                    endpoint.save()

        message = f"Successfully imported schema. Created {created_count} endpoints, updated {updated_count} endpoints."
        return True, message

    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {str(e)}"
    except Exception as e:
        return False, f"Import error: {str(e)}"
