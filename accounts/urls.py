from dj_rest_auth.registration.views import VerifyEmailView
from django.urls import path
from django.urls.conf import include, path

urlpatterns = [
    path("", include('dj_rest_auth.urls')),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('confirm-email/', VerifyEmailView.as_view(),
         name='account_email_verification_sent')

]
