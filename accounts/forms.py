from datetime import date

from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.account.app_settings import (AUTHENTICATION_METHOD,
                                          AuthenticationMethod)
from allauth.account.forms import (EmailAwarePasswordResetTokenGenerator,
                                   ResetPasswordForm, SignupForm)
from allauth.account.utils import user_pk_to_url_str, user_username
from allauth.utils import build_absolute_uri
from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import (ReadOnlyPasswordHashField,
                                       UserChangeForm, UserCreationForm)
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

User = get_user_model()

default_token_generator = EmailAwarePasswordResetTokenGenerator()


def validate_password(self):
    if len(self) < 8:
        raise ValidationError(
            _('Password requires minimum 8 characters.'),
            code='invalid',
        )
    if self.isalpha() or self.isdigit():
        raise ValidationError(
            _('Your password must contain at least one number, one letter, and/or special character.'),
            code='invalid',
        )


def validate_fullname(self):
    fullname = self.split()
    if len(fullname) <= 1:
        raise ValidationError(
            _('Kindly enter more than one name, please.'),
            code='invalid',
            params={'value': self},
        )
    for x in fullname:
        if len(x) < 2:
            raise ValidationError(
                _('Please enter your name correctly.'),
                code='invalid',
                params={'value': self},
            )


class UserAdminCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        strip=True,
        validators=[validate_password],
    )

    name = forms.CharField(
        label=_("Full Name"),
        widget=forms.TextInput,
        strip=True,
        validators=[validate_fullname],
    )

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('name', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (User.objects.filter(email=email.casefold()).exists()):
            raise forms.ValidationError(
                _("This email address is already in use."))
        return email

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"].lower()
        user.name = self.cleaned_data["name"].title()
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}\">this form</a>."
        ),
    )

    name = forms.CharField(
        label=_("Full Name"),
        widget=forms.TextInput,
        strip=True,
        validators=[validate_fullname],
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                'content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')

    def clean_name(self):
        name = self.cleaned_data["name"].title()
        return name

    def clean_email(self):
        if (User.objects.filter(email=self.cleaned_data.get("email").casefold()).exists()):
            raise forms.ValidationError(
                _("This email address is already in use."))
        email = self.cleaned_data["email"].lower()
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.name = self.cleaned_data["name"].title()
        if commit:
            user.save()
        return user


# class MyCustomSignupForm(SignupForm):

#     name = forms.CharField(
#         label=_("Full Name"),
#         widget=forms.TextInput,
#         strip=True,
#         help_text=_(""),
#     )

#     password1 = forms.CharField(
#         label=_("Password"),
#         strip=True,
#         widget=forms.PasswordInput,
#         help_text=_(""),
#         validators=[validate_password],
#     )

#     class Meta:
#         model = User
#         fields = ('name', 'email', 'password1')

#     def save(self, request):

#         # Ensure you call the parent class's save.
#         # .save() returns a User object.
#         user = super(MyCustomSignupForm, self).save(request)

#         # Add your own processing here.

#         # You must return the original result.
#         return user


# class CustomResetPasswordForm(ResetPasswordForm):
#     def save(self, request, **kwargs):
#         current_site = get_current_site(request)
#         email = self.cleaned_data["email"]
#         token_generator = kwargs.get(
#             "token_generator", default_token_generator)

#         for user in self.users:
#             temp_key = token_generator.make_token(user)

#             # save it to the password reset model
#             # password_reset = PasswordReset(user=user, temp_key=temp_key)
#             # password_reset.save()

#             # send the password reset email
#             path = reverse_lazy(
#                 "accounts:reset_password_from_key",
#                 kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
#             )
#             url = build_absolute_uri(request, path)

#             context = {
#                 "current_site": current_site,
#                 "user": user,
#                 "password_reset_url": url,
#                 "request": request,
#             }

#             if AUTHENTICATION_METHOD != AuthenticationMethod.EMAIL:
#                 context["username"] = user_username(user)
#             get_adapter(request).send_mail(
#                 "accounts/email/password_reset_key", email, context
#             )
#         return self.cleaned_data["email"]


# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.sites.shortcuts import get_current_site
# from django.core.mail import EmailMultiAlternatives
# from django.template import loader
# User = get_user_model()


# class RegisterForm(forms.ModelForm):
#     """A form for creating new users. Includes all the required
#     fields, and no repeated password."""
#     error_messages = {
#         'password_mismatch': _("The two password fields didn't match."),
#     }

#     name = forms.CharField(
#         label=_("Full Name"),
#         widget=forms.TextInput,
#         strip=True,
#         help_text=_(""),
#     )

#     password1 = forms.CharField(
#         label=_("Password"),
#         strip=True,
#         widget=forms.PasswordInput,
#         help_text=_(""),
#         validators=[UserAdminCreationForm.validate_password],
#     )

#     class Meta:
#         model = User
#         fields = ('name', 'email',)

#     def save(self, commit=True):
#         # Save the provided password in hashed format
#         user = super(RegisterForm, self).save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         user.email = user.email.lower().strip()
#         user.name = user.name.title()
#         user.active = False  # Send email confirmation via post save signals
#         if commit:
#             user.save()
#         return user


# class ReactivateEmailForm(forms.Form):
#     email = forms.EmailField(max_length=254)

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = EmailActivation.objects.email_exists(email)
#         if not qs.exists():
#             link1 = reverse("contact:contact_home")
#             reconfirm_msg2 = "Kindly <a href='{resend_link}' class='text-info'>contact us to learn more</a>.".format(
#                 resend_link=link1)
#             msg3 = "This email hasn't been registered before or is already activated. " + reconfirm_msg2
#             raise forms.ValidationError(_(mark_safe(msg3)), code='invalid')
#         return email


# class LoginForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)

#     def __init__(self, request, *args, **kwargs):
#         self.request = request
#         super(LoginForm, self).__init__(*args, **kwargs)

#     def clean(self):
#         request = self.request
#         data = self.cleaned_data
#         email = data.get("email")
#         password = data.get("password")
#         user = authenticate(request, username=email, password=password)
#         if user is None:
#             raise forms.ValidationError("Incorrect email address or password!")
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             not_active = qs.filter(active=False)
#             if not_active.exists():
#                 link = reverse("signup_reconfirm_email")
#                 reconfirm_msg = "<a href='{resend_link}' class='text-secondary'>resend confirmation email</a>".format(resend_link=link)
#                 confirm_email = EmailActivation.objects.filter(email=email)
#                 is_confirmable = confirm_email.confirmable().exists()
#                 if is_confirmable:
#                     msg1 = "Your account is not yet confirmed. Kindly check your mail to confirm your account or you can " + reconfirm_msg.lower() + "."
#                     raise forms.ValidationError(mark_safe(msg1))
#                 confirmed_email_exists = EmailActivation.objects.email_exists(email).exists()
#                 if confirmed_email_exists:
#                     msg2 = "Your account is not yet confirmed. Kindly " + reconfirm_msg + " before you can login."
#                     raise forms.ValidationError(_(mark_safe(msg2)), code='invalid')
#                 if not is_confirmable or confirmed_email_exists:
#                     link1 = reverse("contact:contact_home")
#                     reconfirm_msg2 = "Kindly <a href='{resend_link}' class='text-secondary'>contact us for assistance</a>.".format(resend_link=link1)
#                     msg3 = "Your account is inactive. " + reconfirm_msg2
#                     raise forms.ValidationError(_(mark_safe(msg3)), code='invalid')
#         else:
#             link2 = reverse("signup")
#             reconfirm_msg3 = '<a href="{resend_link}" class="text-secondary">join sikademy to login</a>.'.format(resend_link=link2)
#             msg4 = "This email address is not registered yet. Kindly " + reconfirm_msg3
#             raise forms.ValidationError(_(mark_safe(msg4)), code='invalid')
#         login(request, user)
#         self.user = user
#         return data


# class AccountForm(forms.ModelForm):
#     name = forms.CharField(
#         label=_("Full Name"),
#         widget=forms.TextInput,
#         strip=True,
#         help_text=_(""),
#     )
#     email = forms.EmailField()

#     class Meta:
#         model = User
#         fields = ('name', 'email',)

#     def __init__(self, *args, **kwargs):
#         super(AccountForm, self).__init__(*args, **kwargs)
#         self.fields['email'].disabled = True


# class ProfileForm(forms.ModelForm):
#     birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(date.today().year - 4, date.today().year - 100, -1), empty_label=("Choose Year", "Choose Month", "Choose Day")))

#     class Meta:
#         model = Profile
#         fields = ('profile_image', 'username', 'bio', 'location', 'occupation', 'birth_date', 'gender', 'language',
#                   'occupation', 'name_of_organization', 'job_position', 'website', 'linkedin_url', 'github_profile',
#                   'twitter_profile', 'instagram_profile', 'youtube_channel_url'
#                   )
