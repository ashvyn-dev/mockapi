"""Tests for OpenAPI utilities."""

import pytest
from django.contrib.auth.models import User
from domains.models import Collection, MockEndpoint
from domains.openapi_utils import (generate_openapi_schema,
                                   import_openapi_schema,
                                   validate_openapi_schema)


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def collection(db, user):
    """Create a test collection."""
    return Collection.objects.create(
        slug="testapi",
        name="Test API",
        description="Test API Description",
        created_by=user,
    )


@pytest.fixture
def endpoint(db, collection):
    """Create a test endpoint."""
    return MockEndpoint.objects.create(
        collection=collection,
        display_name="Get Users",
        description="Get all users",
        path="users",
        http_method="GET",
        response_status=200,
        content_type="application/json",
        response_body='{"users": []}',
    )


def test_generate_openapi_schema(collection, endpoint):
    """Test OpenAPI schema generation."""
    schema = generate_openapi_schema(collection)

    assert "openapi: 3.0.3" in schema
    assert "Test API" in schema
    assert "/users:" in schema
    assert "get:" in schema


def test_validate_valid_schema():
    """Test validation of valid OpenAPI schema."""
    valid_schema = """
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths:
  /test:
    get:
      summary: Test endpoint
      responses:
        '200':
          description: Success
"""
    is_valid, error = validate_openapi_schema(valid_schema)
    assert is_valid
    assert error == ""


def test_validate_invalid_schema():
    """Test validation of invalid OpenAPI schema."""
    invalid_schema = "not valid yaml: {["
    is_valid, error = validate_openapi_schema(invalid_schema)
    assert not is_valid
    assert "Invalid YAML" in error


def test_validate_missing_required_fields():
    """Test validation when required fields are missing."""
    incomplete_schema = """
openapi: 3.0.3
info:
  title: Test
"""
    is_valid, error = validate_openapi_schema(incomplete_schema)
    assert not is_valid
    assert "paths" in error


def test_import_openapi_schema(collection):
    """Test importing OpenAPI schema."""
    schema = """
openapi: 3.0.3
info:
  title: Imported API
  description: Imported Description
  version: 1.0.0
paths:
  /products:
    get:
      summary: Get Products
      description: Retrieve all products
      responses:
        '200':
          description: Success
          content:
            application/json:
              example:
                products: []
    post:
      summary: Create Product
      responses:
        '201':
          description: Created
"""

    success, message = import_openapi_schema(collection, schema)

    assert success
    assert "Successfully imported" in message

    # Verify endpoints were created
    endpoints = collection.endpoints.all()
    assert endpoints.count() == 2

    get_endpoint = endpoints.filter(http_method="GET", path="products").first()
    assert get_endpoint is not None
    assert get_endpoint.display_name == "Get Products"
    assert get_endpoint.response_status == 200

    post_endpoint = endpoints.filter(http_method="POST", path="products").first()
    assert post_endpoint is not None
    assert post_endpoint.display_name == "Create Product"
    assert post_endpoint.response_status == 201


def test_custom_schema_storage(collection):
    """Test that custom schema is stored and retrieved."""
    custom_schema = (
        "openapi: 3.0.3\ninfo:\n  title: Custom\n  version: 1.0.0\npaths: {}"
    )

    collection.openapi_schema = custom_schema
    collection.save()

    schema = generate_openapi_schema(collection)
    assert schema == custom_schema
