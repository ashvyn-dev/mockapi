#!/usr/bin/env python3

# helpers.py

def get_full_path(mock_endpoint):
    """Get the full path for this endpoint."""
    path = mock_endpoint.path.strip("/")
    return (
        f"/{mock_endpoint.collection.slug}/{path}"
        if path
        else f"/{mock_endpoint.collection.slug}/"
    )

def get_response_headers(mock_endpoint):
    """Get all response headers including custom ones."""
    headers = {
        "Content-Type": mock_endpoint.content_type,
    }
    if mock_endpoint.content_encoding:
        headers["Content-Encoding"] = mock_endpoint.content_encoding

    if mock_endpoint.custom_headers:
        headers.update(mock_endpoint.custom_headers)

    return headers
