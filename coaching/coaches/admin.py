from django.contrib import admin

# Register your models here.
"""
coaching/coaches/admin.py
─────────────────────────
Administración de perfiles de coaches y organizaciones.
Gestión de coaches, especialidades y datos profesionales.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import CoachProfile, Organization


# ═════════════════════════════════════════════════════════════════════════════
# COACH PROFILE ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    """Admin para gestionar perfiles de coaches"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'coach_name',
        'specialty_badge',
        'experience_display',
        'rating_display',
        'session_price_display',
        'total_clients_display',
        'verified_badge',
        'available_badge',
    )
    
    list_filter = (
        'specialty',
        'is_verified',
        'is_available',
        'years_experience',
        'created_at',
    )
    
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'bio',
        'certifications',
    )
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información del Coach
        ('👥 Coach', {
            'fields': ('user',)
        }),
        
        # Información Pública
        ('📋 Información Pública', {
            'fields': (
                'bio',
                'specialty',
                'certifications',
            )
        }),
        
        # Experiencia
        ('⭐ Experiencia y Credibilidad', {
            'fields': (
                ('years_experience', 'rating'),
                'is_verified',
            )
        }),
        
        # Redes Sociales y Web
        ('🌐 Redes Sociales y Web', {
            'fields': (
                'instagram_url',
                'website_url',
            ),
            'classes': ('collapse',)
        }),
        
        # Configuración del Negocio
        ('💼 Configuración del Negocio', {
            'fields': (
                ('session_price', 'session_duration'),
                ('max_clients', 'timezone'),
            )
        }),
        
        # Métricas
        ('📊 Métricas', {
            'fields': (
                ('total_clients', 'avg_compliance'),
                'is_available',
            ),
            'classes': ('collapse',)
        }),
        
        # Timestamps
        ('⏰ Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    
    ordering = ('-created_at',)
    list_per_page = 25
    
    # ── Acciones ───────────────────────────────────────────────
    actions = ['verify_coaches', 'unverify_coaches', 'set_available', 'set_unavailable']
    
    # ── Métodos para el listado ────────────────────────────────
    def coach_name(self, obj):
        """Link al coach (usuario)"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name or obj.user.email)
    coach_name.short_description = 'Coach'
    coach_name.admin_order_field = 'user__first_name'
    
    def specialty_badge(self, obj):
        """Badge de especialidad con colores"""
        colors = {
            'strength': '#e74c3c',
            'hypertrophy': '#3498db',
            'fat_loss': '#2ecc71',
            'powerlifting': '#f39c12',
            'crossfit': '#9b59b6',
            'nutrition': '#27ae60',
            'general': '#95a5a6',
        }
        color = colors.get(obj.specialty, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_specialty_display()
        )
    specialty_badge.short_description = 'Especialidad'
    specialty_badge.admin_order_field = 'specialty'
    
    def experience_display(self, obj):
        """Mostrar experiencia"""
        return f"{obj.years_experience} años"
    experience_display.short_description = 'Experiencia'
    experience_display.admin_order_field = 'years_experience'
    
    def rating_display(self, obj):
        """Mostrar rating con estrellas"""
        if obj.rating > 0:
            stars = '⭐' * int(obj.rating)
            return format_html(
                '<span style="font-size: 1.2em;">{} ({}/5)</span>',
                stars, obj.rating
            )
        return "—"
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def session_price_display(self, obj):
        """Mostrar precio de sesión"""
        return f"${obj.session_price}"
    session_price_display.short_description = 'Precio Sesión'
    session_price_display.admin_order_field = 'session_price'
    
    def total_clients_display(self, obj):
        """Mostrar clientes totales vs máximo"""
        max_clients = obj.max_clients
        percent = int((obj.total_clients / max_clients * 100)) if max_clients > 0 else 0
        
        color = '#27ae60' if percent < 80 else '#f39c12' if percent < 100 else '#e74c3c'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}/{} ({}%)</span>',
            color, obj.total_clients, max_clients, percent
        )
    total_clients_display.short_description = 'Clientes'
    total_clients_display.admin_order_field = 'total_clients'
    
    def verified_badge(self, obj):
        """Badge de verificación"""
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ Verificado</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 3px 8px; border-radius: 3px;">✗ No verificado</span>'
        )
    verified_badge.short_description = 'Verificación'
    verified_badge.admin_order_field = 'is_verified'
    
    def available_badge(self, obj):
        """Badge de disponibilidad"""
        if obj.is_available:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ Disponible</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px;">✗ No disponible</span>'
        )
    available_badge.short_description = 'Disponibilidad'
    available_badge.admin_order_field = 'is_available'
    
    # ── Acciones personalizadas ────────────────────────────────
    def verify_coaches(self, request, queryset):
        """Verificar coaches"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} coach(s) verificado(s).')
    verify_coaches.short_description = '✓ Verificar coaches seleccionados'
    
    def unverify_coaches(self, request, queryset):
        """Desverificar coaches"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} coach(s) desverificado(s).')
    unverify_coaches.short_description = '✗ Desverificar coaches seleccionados'
    
    def set_available(self, request, queryset):
        """Marcar como disponibles"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} coach(s) marcado(s) como disponible.')
    set_available.short_description = '✓ Marcar como Disponible'
    
    def set_unavailable(self, request, queryset):
        """Marcar como no disponibles"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} coach(s) marcado(s) como no disponible.')
    set_unavailable.short_description = '✗ Marcar como No Disponible'


# ═════════════════════════════════════════════════════════════════════════════
# ORGANIZATION ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin para gestionar organizaciones de coaches"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'name',
        'owner_email',
        'slug_display',
        'logo_preview',
        'created_at',
    )
    
    list_filter = (
        'created_at',
    )
    
    search_fields = (
        'name',
        'slug',
        'owner__email',
        'owner__first_name',
        'owner__last_name',
        'description',
    )
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información Básica
        ('📋 Información Básica', {
            'fields': (
                'owner',
                ('name', 'slug'),
            )
        }),
        
        # Logo
        ('🎨 Logo', {
            'fields': (
                'logo',
                'logo_display',
            )
        }),
        
        # Descripción
        ('📝 Descripción', {
            'fields': ('description',)
        }),
        
        # Timestamps
        ('⏰ Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'created_at',
        'logo_display',
    )
    
    prepopulated_fields = {
        'slug': ('name',),
    }
    
    ordering = ('-created_at',)
    list_per_page = 25
    
    # ── Métodos para el listado ────────────────────────────────
    def owner_email(self, obj):
        """Link al propietario (coach)"""
        url = reverse('admin:users_user_change', args=[obj.owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.owner.email)
    owner_email.short_description = 'Propietario (Coach)'
    owner_email.admin_order_field = 'owner__email'
    
    def slug_display(self, obj):
        """Mostrar slug formateado"""
        return format_html(
            '<code style="background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px;">{}</code>',
            obj.slug
        )
    slug_display.short_description = 'Slug'
    slug_display.admin_order_field = 'slug'
    
    def logo_preview(self, obj):
        """Preview del logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 3px;" />',
                obj.logo.url
            )
        return "—"
    logo_preview.short_description = 'Logo'
    
    def logo_display(self, obj):
        """Preview grande del logo en el formulario"""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 5px;" />',
                obj.logo.url
            )
        return "No hay logo"
    logo_display.short_description = 'Preview del Logo'
