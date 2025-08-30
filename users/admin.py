from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

# Define a new Admin class for our CustomUser
class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    # (We are not adding custom forms yet, so we can omit 'add_form' and 'form' if we want to keep it simple for now)

    # The fields to be used in displaying the User model in the admin.
    # These override the definitions on the base UserAdmin
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role') # Added 'role' to filters
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User Role'), {'fields': ('role',)}), # Added our custom 'role' field
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',) # CHANGED FROM 'username' TO 'email'
    filter_horizontal = ('groups', 'user_permissions',)

# Now register the new CustomUserAdmin instead of the default UserAdmin
admin.site.register(CustomUser, CustomUserAdmin)