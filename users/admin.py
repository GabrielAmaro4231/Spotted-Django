from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = [
        'email',
        'name',
        'handle',
        'show_handle_on_leaderboard',
        'is_active',
        'is_staff',
        'is_superuser',
    ]
    list_filter = [
        'show_handle_on_leaderboard',
        'is_active',
        'is_staff',
        'is_superuser',
    ]
    search_fields = ['email', 'name', 'handle']
    filter_horizontal = ['groups', 'user_permissions']
    readonly_fields = ['handle']

    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        (
            'Profile',
            {
                'fields': [
                    'name',
                    'handle',
                    'profile_image_url',
                    'show_handle_on_leaderboard',
                ],
            },
        ),
        (
            'Permissions',
            {
                'fields': [
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ],
            },
        ),
        ('Important dates', {'fields': ['last_login']}),
    ]
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': [
                    'email',
                    'name',
                    'profile_image_url',
                    'show_handle_on_leaderboard',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ],
            },
        ),
    ]
