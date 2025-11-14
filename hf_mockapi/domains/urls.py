from django.urls import path, re_path

from . import views

urlpatterns = [
    # Collection root (e.g., /myproject/)
    path(
        "<slug:collection_slug>/", views.collection_root_handler, name="collection_root"
    ),
    # Collection endpoints (e.g., /myproject/users, /myproject/users/123)
    re_path(
        r"^(?P<collection_slug>[-\w]+)/(?P<endpoint_path>.+)$",
        views.mock_api_handler,
        name="mock_api_handler",
    ),
]
