from django.contrib.auth.models import (AbstractBaseUser, AbstractUser,
                                        PermissionsMixin)
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = None

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=150, default=False)
    active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )

    admin = models.BooleanField(
        _('admin status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without explicitly assigning them.'),
    )

    updated = models.DateField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin

    def has_perms(self, perm, obj=None):
        if self.is_staff:
            return self.staff
        else:
            return self.admin

    def has_perm(self, perm, obj=None):
        return self.admin

    def has_module_perms(self, app_label):
        return True


# def user_presave_protocols(sender, instance, **kwargs):
#     model_email = get_object_or_404(CustomUser, email=instance.email)
#     if str(model_email).casefold() == str(instance.email).casefold():
#         raise ValueError(_("This email address is already in use."))
#     else:
#         instance.email = instance.email.lower()
#         instance.name = instance.name.title()


# models.signals.pre_save.connect(user_presave_protocols, sender=CustomUser)

# @receiver
# def update_last_login(sender, user, **kwargs):
#     """
#     A signal receiver which updates the last_login date for
#     the user logging in.
#     """
#     user.last_login = timezone.now()
#     user.save(update_fields=['last_login'])
