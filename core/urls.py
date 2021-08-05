from accounts.views import CustomPasswordResetConfirmView
from dj_rest_auth.views import PasswordResetConfirmView
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

    # The pasword reset path below can only work
    # if added to the high level urls.py file
    path(
        'api/accounts/password/reset/<slug:uidb64>/<slug:token>/',
        CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),
    path("", include("accounts.urls")),
    path('admin/', admin.site.urls),
]
