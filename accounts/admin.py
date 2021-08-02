from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import CustomUser  # Profile, EmailActivation

User = get_user_model()


# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    add_form = UserAdminCreationForm
    form = UserAdminChangeForm
    # inlines = [
    #     ProfileInline,
    # ]

    fieldsets = (
        # (None, {'fields': ('password',)}), # This simply shows the hashed password field
        (_('Personal info'), {'fields': ('name', 'email',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2')}
         ),
    )
    list_display = ('id', 'email', 'name', 'is_active', 'is_staff')
    list_display_links = ['email']
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'groups')
    search_fields = ('email', 'name')
    ordering = ('email',)
    list_per_page = 10
    filter_horizontal = ('groups', 'user_permissions',)

    # list_select_related = ('profile',)

    # list_select_related = ('profile',)

    # def get_location(self, instance):
    #     return instance.profile.location
    # get_location.short_description = 'Location'

    # def get_username(self, instance):
    #     return instance.profile.username
    # get_username.short_description = 'Username'

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(UserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, UserAdmin)


# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserChangeForm, CustomUserCreationForm
# from .models import CustomUser


# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['email', 'name', ]


# admin.site.register(CustomUser, CustomUserAdmin)
