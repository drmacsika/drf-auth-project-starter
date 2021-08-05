from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup, send_email_confirmation
from allauth.account.views import ConfirmEmailView
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.app_settings import (JWTSerializer, TokenSerializer,
                                       create_token)
from dj_rest_auth.models import TokenModel
from dj_rest_auth.registration.serializers import (SocialAccountSerializer,
                                                   SocialConnectSerializer,
                                                   SocialLoginSerializer,
                                                   VerifyEmailSerializer)
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import PasswordChangeView, PasswordResetConfirmView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.exceptions import (MethodNotAllowed, NotFound,
                                       ValidationError)
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomPasswordSetSerializer, CustomRegisterSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2',
    ),
)


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    email_template_name = 'accounts/registration/password_reset_email.html'


class CustomPasswordSetView(GenericAPIView):
    serializer_class = CustomPasswordSetSerializer
    permission_classes = (IsAuthenticated,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('New password has been saved.')})
