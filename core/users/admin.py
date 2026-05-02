from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de Cuenta', {
            'fields': ('email', 'password', 'is_active')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio')
        }),
        ('Información de Fitness', {
            'fields': ('height', 'weight', 'gender')
        }),
        ('Roles y Permisos', {
            'fields': ('role', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Información de Cuenta (Solo lectura)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )