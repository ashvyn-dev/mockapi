"""
URL configuration for hf_mockapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from domains import views
from domains.api_views import (CollectionViewSet, EndpointResponseViewSet,
                               MockEndpointViewSet, current_user,
                               register_user)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

admin.site.site_header = "HF Mock API Administration"
admin.site.site_title = "HF Mock API"
admin.site.index_title = "Mock Server Manager"

# API Router
router = DefaultRouter()
router.register(r"collections", CollectionViewSet, basename="collection")
router.register(r"endpoints", MockEndpointViewSet, basename="endpoint")
router.register(r"responses", EndpointResponseViewSet, basename="response")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_nested_admin/", include("nested_admin.urls")),
    # API routes (must come before catch-all patterns)
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/register/", register_user, name="register"),
    path("api/auth/me/", current_user, name="current_user"),
    path("api/", include(router.urls)),
    # Mock API catch-all routes (must come last)
    re_path(
        r"^(?P<collection_slug>[-\w]+)/(?P<endpoint_path>.+)$",
        views.mock_api_handler,
        name="mock_api_handler",
    ),
    path(
        "<slug:collection_slug>/", views.collection_root_handler, name="collection_root"
    ),
]
