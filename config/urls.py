from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def test_api_view(request):
    return JsonResponse(
        {
            "status": "success",
            "code": 200,
            "message": "API is working fine!",
        }
    )


urlpatterns = [
    path("test/", test_api_view, name="test-api"), 
    path("admin/", admin.site.urls),
    path("auth_system/", include("auth_system.urls")),
    path("", include("dedup.urls")),
]
