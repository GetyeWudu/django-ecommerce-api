from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.accounts.views import MeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/login/", TokenObtainPairView.as_view(),
         name="token_obtain_pair",),

    path("api/v1/auth/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh",),

    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/catalog/", include("apps.products.urls"))
]
