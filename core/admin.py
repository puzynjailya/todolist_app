from django.contrib import admin
from django.contrib.auth.admin import *
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    fieldsets = (
        ('User data', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')}),
        ('Timestamps', {
            'fields': ('last_login', 'date_joined')}),
        ('Access type', {
            'fields': ('is_staff', 'is_active', 'is_superuser')})
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
