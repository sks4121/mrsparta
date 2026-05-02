"""
fitness/progress/admin.py
─────────────────────────
Administración de registros de progreso y sesiones de entrenamiento.
Seguimiento semanal del avance del atleta.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Sum, Count
from .models import ProgressLog, WorkoutSession


# ═════════════════════════════════════════════════════════════════════════════
# PROGRESS LOG ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    """Admin para gestionar registros de progreso semanal"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'client_email',
        'week_display',
        'date',
        'weight_display',
        'body_fat_display',
        'compliance_display',
        'stagnant_badge',
        'ai_status',
    )
    
    list_filter = (
        'is_stagnant',
        'ai_analyzed',
        'ai_alert_sent',
        ('date', admin.DateFieldListFilter),
        'week_number',
    )
    
    search_fields = (
        'client__email',
        'client__first_name',
        'client__last_name',
        'notes',
        'coach_notes',
    )
    
    date_hierarchy = 'date'
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información Básica
        ('📋 Información Básica', {
            'fields': (
                'client',
                ('plan', 'week_number'),
                'date',
            )
        }),
        
        # Métricas de Peso y Cuerpo
        ('⚖️ Peso y Cuerpo', {
            'fields': (
                ('weight_kg', 'body_fat_pct'),
                ('muscle_mass_kg',),
                ('waist_cm', 'chest_cm'),
                ('hip_cm', 'arm_cm'),
            )
        }),
        
        # Cumplimiento
        ('✅ Cumplimiento (%)', {
            'fields': (
                ('training_compliance', 'nutrition_compliance', 'hydration_compliance'),
            ),
            'description': 'Porcentaje de cumplimiento (0-100%).'
        }),
        
        # Energía y Bienestar
        ('🌟 Energía y Bienestar', {
            'fields': (
                ('energy_level', 'sleep_hours', 'stress_level'),
            ),
            'description': 'Escala 1-10 para energía y estrés. Horas de sueño en decimal.'
        }),
        
        # Notas
        ('📝 Notas', {
            'fields': (
                'notes',
                'coach_notes',
            )
        }),
        
        # IA
        ('🤖 IA Engine', {
            'fields': (
                'is_stagnant',
                'ai_analyzed',
                'ai_alert_sent',
            ),
            'classes': ('collapse',),
            'description': 'Flags del AI Engine para detección de estancamiento.'
        }),
        
        # Timestamps
        ('📅 Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'created_at',
        'is_stagnant',
        'ai_analyzed',
        'ai_alert_sent',
    )
    
    ordering = ('-date',)
    list_per_page = 30
    
    # ── Acciones ───────────────────────────────────────────────
    actions = ['mark_analyzed', 'mark_stagnant', 'mark_alert_sent']
    
    # ── Métodos para el listado ────────────────────────────────
    def client_email(self, obj):
        """Link al cliente"""
        url = reverse('admin:users_user_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.email)
    client_email.short_description = 'Cliente'
    client_email.admin_order_field = 'client__email'
    
    def week_display(self, obj):
        """Mostrar semana"""
        return f"Sem {obj.week_number}"
    week_display.short_description = 'Semana'
    week_display.admin_order_field = 'week_number'
    
    def weight_display(self, obj):
        """Mostrar peso"""
        if obj.weight_kg:
            return f"{obj.weight_kg} kg"
        return "—"
    weight_display.short_description = 'Peso'
    weight_display.admin_order_field = 'weight_kg'
    
    def body_fat_display(self, obj):
        """Mostrar grasa corporal"""
        if obj.body_fat_pct:
            return f"{obj.body_fat_pct}%"
        return "—"
    body_fat_display.short_description = 'Grasa'
    body_fat_display.admin_order_field = 'body_fat_pct'
    
    def compliance_display(self, obj):
        """Mostrar cumplimiento overall"""
        compliance = obj.overall_compliance
        
        if compliance >= 80:
            color = '#27ae60'
        elif compliance >= 60:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}%</span>',
            color, compliance
        )
    compliance_display.short_description = 'Cumplimiento'
    compliance_display.admin_order_field = 'training_compliance'
    
    def stagnant_badge(self, obj):
        """Badge de estancamiento"""
        if obj.is_stagnant:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px;">⚠️ Estancado</span>'
            )
        return format_html(
            '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ Normal</span>'
        )
    stagnant_badge.short_description = 'Estado'
    stagnant_badge.admin_order_field = 'is_stagnant'
    
    def ai_status(self, obj):
        """Mostrar estado del AI"""
        status = []
        if obj.ai_analyzed:
            status.append('🤖 Analizado')
        if obj.ai_alert_sent:
            status.append('🔔 Alerta')
        
        if status:
            return ' · '.join(status)
        return "—"
    ai_status.short_description = 'IA'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_analyzed(self, request, queryset):
        """Marcar como analizado"""
        updated = queryset.update(ai_analyzed=True)
        self.message_user(request, f'{updated} registro(s) marcado(s) como analizado.')
    mark_analyzed.short_description = '🤖 Marcar como Analizado'
    
    def mark_stagnant(self, request, queryset):
        """Marcar como estancado"""
        updated = queryset.update(is_stagnant=True)
        self.message_user(request, f'{updated} registro(s) marcado(s) como estancado.')
    mark_stagnant.short_description = '⚠️ Marcar como Estancado'
    
    def mark_alert_sent(self, request, queryset):
        """Marcar como alerta enviada"""
        updated = queryset.update(ai_alert_sent=True)
        self.message_user(request, f'{updated} alerta(s) marcada(s) como enviada.')
    mark_alert_sent.short_description = '🔔 Marcar como Alerta Enviada'


# ═════════════════════════════════════════════════════════════════════════════
# WORKOUT SESSION ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """Admin para gestionar sesiones de entrenamiento completadas"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'client_email',
        'training_day_link',
        'date',
        'status_badge',
        'duration_display',
        'rpe_display',
        'created_at',
    )
    
    list_filter = (
        'status',
        ('date', admin.DateFieldListFilter),
        'rpe_avg',
    )
    
    search_fields = (
        'client__email',
        'client__first_name',
        'client__last_name',
        'training_day__focus',
        'notes',
    )
    
    date_hierarchy = 'date'
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información
        ('📋 Información', {
            'fields': (
                'client',
                'training_day',
                'date',
            )
        }),
        
        # Detalles de la Sesión
        ('💪 Detalles', {
            'fields': (
                'status',
                ('duration_min', 'rpe_avg'),
            )
        }),
        
        # Notas
        ('📝 Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        
        # Timestamps
        ('📅 Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    ordering = ('-date',)
    list_per_page = 50
    
    # ── Acciones ───────────────────────────────────────────────
    actions = ['mark_completed', 'mark_partial', 'mark_skipped']
    
    # ── Métodos para el listado ────────────────────────────────
    def client_email(self, obj):
        """Link al cliente"""
        url = reverse('admin:users_user_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.email)
    client_email.short_description = 'Cliente'
    client_email.admin_order_field = 'client__email'
    
    def training_day_link(self, obj):
        """Link al día de entrenamiento"""
        if obj.training_day:
            url = reverse('admin:plans_trainingday_change', args=[obj.training_day.id])
            return format_html('<a href="{}">{} ({})</a>', url, obj.training_day.day_name, obj.training_day.focus)
        return "—"
    training_day_link.short_description = 'Día'
    
    def status_badge(self, obj):
        """Badge de estado"""
        colors = {
            'completed': '#27ae60',
            'partial': '#f39c12',
            'skipped': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def duration_display(self, obj):
        """Mostrar duración"""
        if obj.duration_min:
            return f"{obj.duration_min} min"
        return "—"
    duration_display.short_description = 'Duración'
    duration_display.admin_order_field = 'duration_min'
    
    def rpe_display(self, obj):
        """Mostrar RPE promedio con color"""
        if obj.rpe_avg:
            if obj.rpe_avg >= 8:
                color = '#e74c3c'
            elif obj.rpe_avg >= 6:
                color = '#f39c12'
            else:
                color = '#27ae60'
            
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}/10</span>',
                color, obj.rpe_avg
            )
        return "—"
    rpe_display.short_description = 'RPE'
    rpe_display.admin_order_field = 'rpe_avg'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_completed(self, request, queryset):
        """Marcar como completada"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} sesión(es) marcada(s) como completada.')
    mark_completed.short_description = '✓ Marcar como Completada'
    
    def mark_partial(self, request, queryset):
        """Marcar como parcial"""
        updated = queryset.update(status='partial')
        self.message_user(request, f'{updated} sesión(es) marcada(s) como parcial.')
    mark_partial.short_description = '⚠️ Marcar como Parcial'
    
    def mark_skipped(self, request, queryset):
        """Marcar como saltada"""
        updated = queryset.update(status='skipped')
        self.message_user(request, f'{updated} sesión(es) marcada(s) como saltada.')
    mark_skipped.short_description = '✗ Marcar como Saltada'