from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
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
from dj_rest_auth.views import (LoginView, PasswordChangeView,
                                PasswordResetConfirmView)
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.dispatch import receiver
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import (APIException, MethodNotAllowed,
                                       NotFound, ValidationError)
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (CustomEmailConfirmationSerializer,
                          CustomLoginSerializer, CustomPasswordSetSerializer,
                          CustomRegisterSerializer)

User = get_user_model()

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2',
    ),
)


class CustomLoginView(LoginView):
    serializer_class = CustomLoginSerializer


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


class CustomEmailConfirmationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomEmailConfirmationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            email = EmailAddress.objects.get(**serializer.validated_data)
        except:
            return Response({'email': _("Account does not exist")}, status=status.HTTP_400_BAD_REQUEST)

        if email.verified:
            return Response({'email': _("Account is already verified")}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            send_email_confirmation(request, user=user)
            return Response({'email': _('Email confirmation sent!')}, status=status.HTTP_200_OK)
        except:
            return Response({'email': _('Something went wrong while sending you an email.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
