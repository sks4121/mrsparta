"""
fitness/profiles/admin.py
─────────────────────────
Administración del perfil de atletas en Django Admin.
Permite ver, crear y editar perfiles de clientes.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """
    Admin personalizado para ClientProfile.
    Interfaz completa para gestionar perfiles de atletas.
    """
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'user_email',
        'coach_display',
        'goal',
        'level',
        'weight_display',
        'bmi_display',
        'is_active',
        'joined_at',
    )
    
    list_filter = (
        'goal',
        'level',
        'activity_level',
        'is_active',
        'joined_at',
        'subscription_plan',
    )
    
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'coach__email',
    )
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información del Usuario y Coach
        ('👤 Usuario y Coach', {
            'fields': ('user', 'coach'),
            'description': 'Vinculación del perfil con el usuario y su entrenador.'
        }),
        
        # Datos Físicos Actuales
        ('💪 Datos Físicos Actuales', {
            'fields': (
                'weight_kg',
                'height_cm',
                'age',
                'body_fat_pct',
            ),
            'description': 'Medidas actuales del atleta.'
        }),
        
        # Objetivos y Nivel
        ('🎯 Objetivos y Nivel', {
            'fields': (
                'goal',
                'target_weight',
                'level',
                'activity_level',
            ),
            'description': 'Objetivos y nivel de entrenamiento del atleta.'
        }),
        
        # Métricas Calculadas (Solo lectura)
        ('📊 Métricas Calculadas', {
            'fields': (
                'bmi',
                'bmr_kcal',
                'tdee_kcal',
            ),
            'classes': ('collapse',),
            'description': 'Métricas calculadas automáticamente (solo lectura).'
        }),
        
        # Información Médica
        ('⚕️ Información Médica', {
            'fields': (
                'injuries',
                'medications',
            ),
            'classes': ('collapse',),
            'description': 'Lesiones, limitaciones y medicaciones relevantes.'
        }),
        
        # Equipamiento y Notas
        ('🏋️ Equipamiento y Notas', {
            'fields': (
                'equipment',
                'notes',
            ),
            'classes': ('collapse',),
        }),
        
        # Estado y Suscripción
        ('💳 Estado y Suscripción', {
            'fields': (
                'subscription_plan',
                'is_active',
            ),
        }),
        
        # Timestamps (Solo lectura)
        ('📅 Timestamps', {
            'fields': (
                'joined_at',
                'updated_at',
            ),
            'classes': ('collapse',),
            'description': 'Fechas de creación y última actualización (solo lectura).'
        }),
    )
    
    # ── Campos de solo lectura ─────────────────────────────────
    readonly_fields = (
        'bmi',
        'bmr_kcal',
        'tdee_kcal',
        'joined_at',
        'updated_at',
    )
    
    # ── Configuración de ordenamiento ──────────────────────────
    ordering = ('-joined_at',)
    
    # ── Paginación ─────────────────────────────────────────────
    list_per_page = 25
    
    # ── Acciones en el listado ─────────────────────────────────
    actions = ['activate_profiles', 'deactivate_profiles', 'set_basic_plan', 'set_premium_plan']
    
    # ── Métodos para el listado ────────────────────────────────
    def user_email(self, obj):
        """Mostrar email del usuario en el listado"""
        return obj.user.email
    user_email.short_description = 'Email del Usuario'
    user_email.admin_order_field = 'user__email'
    
    def coach_display(self, obj):
        """Mostrar coach del usuario o 'Sin asignar'"""
        if obj.coach:
            return f"{obj.coach.get_full_name() or obj.coach.email}"
        return format_html('<span style="color: red;">Sin asignar</span>')
    coach_display.short_description = 'Entrenador'
    coach_display.admin_order_field = 'coach__email'
    
    def weight_display(self, obj):
        """Mostrar peso de forma legible"""
        if obj.weight_kg:
            return f"{obj.weight_kg} kg"
        return "-"
    weight_display.short_description = 'Peso'
    weight_display.admin_order_field = 'weight_kg'
    
    def bmi_display(self, obj):
        """Mostrar BMI con color según rango"""
        if not obj.bmi:
            return "-"
        
        bmi = float(obj.bmi)
        if bmi < 18.5:
            color = 'blue'
            category = 'Bajo peso'
        elif 18.5 <= bmi < 25:
            color = 'green'
            category = 'Normal'
        elif 25 <= bmi < 30:
            color = 'orange'
            category = 'Sobrepeso'
        else:
            color = 'red'
            category = 'Obeso'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color, obj.bmi, category
        )
    bmi_display.short_description = 'IMC'
    bmi_display.admin_order_field = 'bmi'
    
    # ── Acciones personalizadas ────────────────────────────────
    def activate_profiles(self, request, queryset):
        """Activar perfiles seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} perfil(es) activado(s).')
    activate_profiles.short_description = '✅ Activar perfiles seleccionados'
    
    def deactivate_profiles(self, request, queryset):
        """Desactivar perfiles seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} perfil(es) desactivado(s).')
    deactivate_profiles.short_description = '❌ Desactivar perfiles seleccionados'
    
    def set_basic_plan(self, request, queryset):
        """Establecer plan básico"""
        updated = queryset.update(subscription_plan='basic')
        self.message_user(request, f'{updated} perfil(es) a plan BÁSICO.')
    set_basic_plan.short_description = '💳 Establecer plan BÁSICO'
    
    def set_premium_plan(self, request, queryset):
        """Establecer plan premium"""
        updated = queryset.update(subscription_plan='premium')
        self.message_user(request, f'{updated} perfil(es) a plan PREMIUM.')
    set_premium_plan.short_description = '💎 Establecer plan PREMIUM'
    
    # ── Personalización del formulario ─────────────────────────
    def get_readonly_fields(self, request, obj=None):
        """Si es creación nueva, permitir editar todos los campos"""
        if obj:
            return self.readonly_fields
        return []
    
    def save_model(self, request, obj, form, change):
        """Hook al guardar el modelo"""
        if not change:
            # Si es nuevo, el BMI se calcula automáticamente
            pass
        super().save_model(request, obj, form, change)