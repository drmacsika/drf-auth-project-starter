from django.contrib import admin
from django.urls import path
from django.urls.conf import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

urlpatterns = [

    # Simple JWT
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/token/verify/", TokenVerifyView.as_view()),

    # rest_framework
    path('api/', include('rest_framework.urls')),
    path("api/accounts/", include("accounts.urls")),
    path('admin/', admin.site.urls),
]
