from django.urls import path

from .views import RegisterView, MeView,LogoutView,PasswordChangeView,PasswordResetRequestView


urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    path(
        "password_reset_request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
]