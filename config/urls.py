
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth_system/', include('auth_system.urls')),
    path('dedup/', include('dedup.urls')),
]
