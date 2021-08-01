from core.utils import get_first_name, get_last_name
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserQuerySet(models.QuerySet):
    pass


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _create_user(self, name, email, password, **extra_fields):
        """
        Create and save a user with the given name, email, and password.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))

        fullname = name.split()
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
        email = self.normalize_email(email)
        name = ' '.join(map(str, fullname))
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, name, email=None, password=None, **extra_fields):
        extra_fields.setdefault('staff', False)
        extra_fields.setdefault('admin', False)
        return self._create_user(name, email, password, **extra_fields)

    def create_staff(self, name, email, password, **extra_fields):
        extra_fields.setdefault('staff', True)
        extra_fields.setdefault('admin', False)

        if extra_fields.get('staff') is not True:
            raise ValueError('Staff must have staff=True.')

        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault('staff', True)
        extra_fields.setdefault('admin', True)

        if extra_fields.get('staff') is not True:
            raise ValueError('Admin must have staff=True.')
        if extra_fields.get('admin') is not True:
            raise ValueError('Admin must have admin=True.')

        return self._create_user(name, email, password, **extra_fields)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return get_first_name(self.name)

    def get_first_name(self):
        return get_first_name(self.name)

    def get_last_name(self):
        return get_last_name(self.name)
    