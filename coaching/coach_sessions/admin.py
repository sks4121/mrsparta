"""
coaching/coach_sessions/admin.py
────────────────────────────────
Administración de sesiones y reservas de coaching.
Gestión de videollamadas, sesiones presenciales y chequeos.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count
from .models import CoachSession


@admin.register(CoachSession)
class CoachSessionAdmin(admin.ModelAdmin):
    """Admin para gestionar sesiones de coaching"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'session_summary',
        'coach_email',
        'client_email',
        'type_badge',
        'status_badge',
        'scheduled_at',
        'price_display',
        'duration_display',
    )
    
    list_filter = (
        'session_type',
        'status',
        ('scheduled_at', admin.DateFieldListFilter),
        'coach',
    )
    
    search_fields = (
        'coach__email',
        'coach__first_name',
        'coach__last_name',
        'client__email',
        'client__first_name',
        'client__last_name',
        'notes_coach',
        'notes_client',
        'meeting_url',
    )
    
    date_hierarchy = 'scheduled_at'
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información Básica
        ('👥 Participantes', {
            'fields': (
                ('coach', 'client'),
            )
        }),
        
        # Detalles de la Sesión
        ('📅 Detalles de la Sesión', {
            'fields': (
                'session_type',
                'status',
                ('scheduled_at', 'duration_min'),
                'completed_at',
            )
        }),
        
        # Acceso a la Sesión
        ('🔗 Acceso', {
            'fields': (
                'meeting_url',
                'recording_url',
            ),
            'description': 'Links de acceso a la sesión (Zoom/Meet) y grabación.'
        }),
        
        # Precios
        ('💰 Precios', {
            'fields': ('price',)
        }),
        
        # Notas del Coach
        ('📝 Notas del Coach', {
            'fields': ('notes_coach',),
            'classes': ('collapse',)
        }),
        
        # Notas del Cliente
        ('📝 Notas del Cliente', {
            'fields': ('notes_client',),
            'classes': ('collapse',)
        }),
        
        # Timestamps
        ('⏰ Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'created_at',
    )
    
    ordering = ('-scheduled_at',)
    list_per_page = 50
    
    # ── Acciones ───────────────────────────────────────────────
    actions = [
        'mark_completed',
        'mark_cancelled',
        'mark_no_show',
        'send_reminder',
    ]
    
    # ── Métodos para el listado ────────────────────────────────
    def session_summary(self, obj):
        """Resumen de la sesión"""
        day_name = obj.scheduled_at.strftime('%a')
        time = obj.scheduled_at.strftime('%H:%M')
        return f"{day_name} {time}"
    session_summary.short_description = 'Hora'
    session_summary.admin_order_field = 'scheduled_at'
    
    def coach_email(self, obj):
        """Link al coach"""
        url = reverse('admin:users_user_change', args=[obj.coach.id])
        return format_html('<a href="{}">{}</a>', url, obj.coach.email)
    coach_email.short_description = 'Coach'
    coach_email.admin_order_field = 'coach__email'
    
    def client_email(self, obj):
        """Link al cliente"""
        url = reverse('admin:users_user_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.email)
    client_email.short_description = 'Cliente'
    client_email.admin_order_field = 'client__email'
    
    def type_badge(self, obj):
        """Badge del tipo de sesión"""
        colors = {
            'video_call': '#3498db',
            'presential': '#2ecc71',
            'monthly_check': '#9b59b6',
            'initial': '#f39c12',
        }
        color = colors.get(obj.session_type, '#95a5a6')
        icons = {
            'video_call': '📹',
            'presential': '👤',
            'monthly_check': '📊',
            'initial': '📋',
        }
        icon = icons.get(obj.session_type, '📅')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{} {}</span>',
            color, icon, obj.get_session_type_display()
        )
    type_badge.short_description = 'Tipo'
    type_badge.admin_order_field = 'session_type'
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        # Determinar si está en el pasado o futuro
        now = timezone.now()
        is_past = obj.scheduled_at < now
        
        colors = {
            'scheduled': '#3498db' if not is_past else '#95a5a6',
            'completed': '#27ae60',
            'cancelled': '#e74c3c',
            'no_show': '#f39c12',
        }
        color = colors.get(obj.status, '#95a5a6')
        
        # Agregar indicador de "próxima"
        extra = ""
        if obj.status == 'scheduled' and not is_past:
            extra = " (Próxima)"
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}{}</span>',
            color, obj.get_status_display(), extra
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def price_display(self, obj):
        """Mostrar precio"""
        if obj.price > 0:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">${}</span>',
                obj.price
            )
        return "Gratis"
    price_display.short_description = 'Precio'
    price_display.admin_order_field = 'price'
    
    def duration_display(self, obj):
        """Mostrar duración"""
        return f"{obj.duration_min} min"
    duration_display.short_description = 'Duración'
    duration_display.admin_order_field = 'duration_min'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_completed(self, request, queryset):
        """Marcar como completada"""
        from django.utils import timezone
        updated_count = 0
        for session in queryset:
            if session.status != 'completed':
                session.status = 'completed'
                session.completed_at = timezone.now()
                session.save()
                updated_count += 1
        
        self.message_user(request, f'{updated_count} sesión(es) marcada(s) como completada.')
    mark_completed.short_description = '✓ Marcar como Completada'
    
    def mark_cancelled(self, request, queryset):
        """Marcar como cancelada"""
        updated = queryset.filter(status='scheduled').update(status='cancelled')
        self.message_user(request, f'{updated} sesión(es) cancelada(s).')
    mark_cancelled.short_description = '✗ Marcar como Cancelada'
    
    def mark_no_show(self, request, queryset):
        """Marcar como no asistió"""
        updated = queryset.filter(status='scheduled').update(status='no_show')
        self.message_user(request, f'{updated} sesión(es) marcada(s) como no asistió.')
    mark_no_show.short_description = '⚠️ Marcar como No Asistió'
    
    def send_reminder(self, request, queryset):
        """Enviar recordatorio (acción simulada)"""
        # En producción, integrar con servicio de email/SMS
        upcoming = queryset.filter(
            status='scheduled',
            scheduled_at__gt=timezone.now()
        ).count()
        
        if upcoming > 0:
            self.message_user(request, f'Recordatorio enviado a {upcoming} sesión(es).')
        else:
            self.message_user(request, 'No hay sesiones próximas para recordar.', level='warning')
    send_reminder.short_description = '🔔 Enviar Recordatorio'
    
    # ── Personalización de cambios ─────────────────────────────
    def get_readonly_fields(self, request, obj=None):
        """Campos readonly en edición"""
        if obj:
            return self.readonly_fields + ['created_at', 'completed_at']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Hook al guardar"""
        super().save_model(request, obj, form, change)
    
    # ── Personalización de queryset ────────────────────────────
    def get_queryset(self, request):
        """Optimizar queryset con select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('coach', 'client')
    
    # ── Cambios en el formulario ───────────────────────────────
    def change_form_base_template(self):
        return 'admin/change_form.html'
    
    def get_form(self, request, obj=None, **kwargs):
        """Customizar forma según el contexto"""
        form = super().get_form(request, obj, **kwargs)
        
        # Limitar coaches a coaches reales
        form.base_fields['coach'].queryset = form.base_fields['coach'].queryset.filter(role='coach')
        
        # Limitar clientes a atletas reales
        form.base_fields['client'].queryset = form.base_fields['client'].queryset.filter(role='athlete')
        
        return form


# ═════════════════════════════════════════════════════════════════════════════
# CUSTOM ADMIN SITE CONFIGURATION (Opcional)
# ═════════════════════════════════════════════════════════════════════════════

# Si quieres agregar un título personalizado a la sección de coaching:
"""
Para personalizar aún más, puedes modificar el sitio admin:

En coaching/apps.py:

class CoachingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coaching'
    verbose_name = '⚡ Coaching y Sesiones'
"""
