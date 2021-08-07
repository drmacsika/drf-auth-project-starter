from dj_rest_auth.registration.views import ConfirmEmailView, VerifyEmailView
from django.urls import path
from django.urls.conf import include, path

from .views import (CustomEmailConfirmationView, CustomLoginView,
                    CustomPasswordSetView, CustomRegisterView)

app_name = "accounts"

urlpatterns = [
    path("api/accounts/", include('dj_rest_auth.urls')),
    # The path below should always be placed above the signup view.
    path(
        'api/accounts/confirm-email/<str:key>/',
        ConfirmEmailView.as_view(), name='confirm_email',
    ),
    path("api/accounts/signin/",
         CustomLoginView.as_view(), name="login"),
    path("api/accounts/password/set/",
         CustomPasswordSetView.as_view(), name="set_password"),
    path('api/accounts/signup/', CustomRegisterView.as_view(),
         name='signup'),
    path('api/accounts/confirm-email/', VerifyEmailView.as_view(),
         name='email_verification_sent'),
    path('api/accounts/resend-email/',
         CustomEmailConfirmationView.as_view(), name="resend_email"),

]


# urlpatterns = [
#     path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
#     path('signup/', SignupView.as_view(template_name='accounts/signup.html'), name='signup'),
#     path('confirm-email/', EmailVerificationSentView.as_view(template_name="accounts/verification_sent.html"),
#          name='email_verification_sent'),
#     re_path(r"^confirm-email/(?P<key>[-:\w]+)/$", ConfirmEmailView.as_view(
#         template_name='accounts/email_confirm.html'), name='confirm_email'),
#     path('logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
#     path("password/change/", CustomPasswordChangeView.as_view(),
#          name="change_password"),
# path("password/set/", CustomPasswordSetView.as_view(), name="set_password"),
#     path("password/reset/", CustomPasswordResetView.as_view(), name="reset_password"),
#     path(
#         "password/reset/done/", PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name="reset_password_done",
#     ),
#     re_path(
#         r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", CustomPasswordResetFromKeyView.as_view(), name="reset_password_from_key",
#     ),
#     path(
#         "password/reset/key/done/", PasswordResetFromKeyDoneView.as_view(template_name='accounts/password_reset_from_key_done.html'), name="reset_password_from_key_done",
#     ),
