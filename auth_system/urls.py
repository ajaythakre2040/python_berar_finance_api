from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from auth_system.views.auth_view import (
    RegisterView,
    LoginView,
    LogoutView,
)
from auth_system.views.user_view import UserDetailUpdateDeleteView, UserListView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path(
        "users/<int:id>/",
        UserDetailUpdateDeleteView.as_view(),
        name="user-detail-update-delete",
    ),
]
