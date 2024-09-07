from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_no')
    ordering = ('email',)
    readonly_fields = ('referrer_id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ( 'username', 'first_name', 'last_name', 'phone_no', 'referrer_id','referred_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_verified', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',  'username', 'first_name', 'last_name', 'phone_no', 'password1', 'password2', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)

