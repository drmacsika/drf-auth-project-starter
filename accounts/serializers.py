from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from requests.exceptions import HTTPError
from rest_framework import serializers
from rest_framework.reverse import reverse

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.utils import email_address_exists, get_username_max_length
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction

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
