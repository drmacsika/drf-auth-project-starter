from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest
from django.urls import exceptions as url_exceptions
from django.urls.exceptions import NoReverseMatch
from django.utils.encoding import force_str
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from requests.exceptions import HTTPError
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.reverse import reverse

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.forms import AddEmailForm
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.utils import email_address_exists, get_username_max_length
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction

from .forms import CustomSetPasswordForm

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(required=False)

    def validate_fullname(self, fullname):
        fullname = fullname.split()
        if len(fullname) <= 1:
            raise serializers.ValidationError(
                _('Kindly enter more than one name.'),)
        for x in fullname:
            if len(x) < 2:
                raise serializers.ValidationError(
                    _('Kindly give us your full name.'),)
        return fullname

    def get_cleaned_data(self):
        return {
            'name': self.validated_data.get('name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def validate(self, data):
        # if data['password1'] != data['password1']:
        #     raise serializers.ValidationError(
        #         _("The two password fields didn't match."))
        fullname = data['name'].split()
        if len(fullname) <= 1:
            raise serializers.ValidationError(
                _('Kindly enter more than one name.'),)
        for x in fullname:
            if len(x) < 2:
                raise serializers.ValidationError(
                    _('Kindly give us your full name.'),)
        return data

    # Define transaction.atomic to rollback the save operation in case of error
    # @transaction.atomic
    # def save(self, request):
    #     user = super().save(request)
    #     user.name = self.data.get('name')
    #     user.save()
    #     return user

    @transaction.atomic
    def save(self, request):
        # user = super().save(*args, **kwargs)
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        try:
            adapter.clean_password(self.cleaned_data['password1'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                detail=serializers.as_serializer_error(exc)
            )
        user.name = self.cleaned_data["name"].title()
        user.save()
        setup_user_email(request, user, [])
        return user


class CustomUserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'name',
        )
        read_only_fields = ('email',)


class CustomPasswordSetSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm
    set_password_form = None

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)
        if self.request.user.has_usable_password():
            # return HttpResponseRedirect(reverse("account_change_password"))
            change_password_link = "<a href=\"http://127.0.0.1:3000/change-password\""
            err_msg = _(
                f'You\'ve already set a password for this account. To change your password visit {change_password_link}')
            raise serializers.ValidationError(err_msg)

    def validate_old_password(self, value):
        pass

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.request, self.user)
