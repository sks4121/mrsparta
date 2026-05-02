"""
fitness/plans/admin.py
──────────────────────
Administración de planes de entrenamiento y nutrición.
Gestión de semanas, días, ejercicios y comidas.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import Plan, TrainingDay, Exercise, Meal


# ═════════════════════════════════════════════════════════════════════════════
# INLINES — Edición en línea dentro del formulario padre
# ═════════════════════════════════════════════════════════════════════════════

class TrainingDayInline(admin.TabularInline):
    """Inline para editar días de entrenamiento dentro de un Plan"""
    model = TrainingDay
    extra = 0
    fields = ('day_name', 'focus', 'is_rest_day', 'order', 'notes')
    ordering = ('order',)


class ExerciseInline(admin.TabularInline):
    """Inline para editar ejercicios dentro de un TrainingDay"""
    model = Exercise
    extra = 0
    fields = ('name', 'sets', 'reps', 'weight_kg', 'rest_seconds', 'rpe', 'order', 'is_completed')
    ordering = ('order',)


class MealInline(admin.TabularInline):
    """Inline para editar comidas dentro de un Plan"""
    model = Meal
    extra = 0
    fields = ('meal_type', 'name', 'calories', 'protein_g', 'carbs_g', 'fat_g', 'order')
    ordering = ('order',)


# ═════════════════════════════════════════════════════════════════════════════
# PLAN ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin para gestionar planes de entrenamiento y nutrición"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'name',
        'client_email',
        'plan_type_badge',
        'status_badge',
        'week_progress',
        'created_by',
        'start_date',
    )
    
    list_filter = (
        'plan_type',
        'status',
        'created_by',
        'start_date',
        'created_at',
    )
    
    search_fields = (
        'name',
        'client__email',
        'client__first_name',
        'client__last_name',
        'coach__email',
    )
    
    # ── Inlines ────────────────────────────────────────────────
    inlines = [TrainingDayInline, MealInline]
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información General
        ('📋 Información General', {
            'fields': ('name', 'description', 'plan_type', 'status', 'created_by')
        }),
        
        # Vinculación
        ('👥 Vinculación', {
            'fields': ('client', 'coach')
        }),
        
        # Temporalidad
        ('📅 Temporalidad', {
            'fields': (
                ('week_number', 'total_weeks'),
                ('start_date', 'end_date'),
            )
        }),
        
        # Objetivos
        ('🎯 Objetivos', {
            'fields': ('goals_notes',),
            'classes': ('collapse',)
        }),
        
        # Nutrición
        ('🍎 Resumen Nutricional', {
            'fields': (
                ('daily_calories',),
                ('protein_g', 'carbs_g', 'fat_g'),
                ('water_liters',),
            ),
            'classes': ('collapse',)
        }),
        
        # Timestamps
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    ordering = ('-created_at',)
    list_per_page = 25
    
    # ── Métodos para el listado ────────────────────────────────
    def client_email(self, obj):
        """Mostrar email del cliente"""
        return obj.client.email
    client_email.short_description = 'Cliente'
    client_email.admin_order_field = 'client__email'
    
    def plan_type_badge(self, obj):
        """Badge de tipo de plan"""
        colors = {
            'training': '#3498db',
            'nutrition': '#2ecc71',
            'combined': '#9b59b6',
        }
        color = colors.get(obj.plan_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_plan_type_display()
        )
    plan_type_badge.short_description = 'Tipo'
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        colors = {
            'draft': '#95a5a6',
            'active': '#27ae60',
            'paused': '#f39c12',
            'done': '#2c3e50',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def week_progress(self, obj):
        """Mostrar progreso de semanas"""
        return f"Sem {obj.week_number}/{obj.total_weeks}"
    week_progress.short_description = 'Semana'
    week_progress.admin_order_field = 'week_number'


# ═════════════════════════════════════════════════════════════════════════════
# TRAINING DAY ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(TrainingDay)
class TrainingDayAdmin(admin.ModelAdmin):
    """Admin para gestionar días de entrenamiento"""
    
    list_display = (
        'day_name',
        'plan_link',
        'focus',
        'exercise_count',
        'rest_day_badge',
        'order',
    )
    
    list_filter = (
        'day_name',
        'is_rest_day',
        'plan__client',
    )
    
    search_fields = (
        'focus',
        'plan__name',
        'plan__client__email',
    )
    
    inlines = [ExerciseInline]
    
    fieldsets = (
        ('📅 Información', {
            'fields': ('plan', 'day_name', 'order')
        }),
        ('💪 Detalles', {
            'fields': ('focus', 'is_rest_day', 'notes')
        }),
    )
    
    ordering = ('plan', 'order')
    list_per_page = 50
    
    def plan_link(self, obj):
        """Link al plan padre"""
        url = reverse('admin:plans_plan_change', args=[obj.plan.id])
        return format_html('<a href="{}">{}</a>', url, obj.plan.name)
    plan_link.short_description = 'Plan'
    
    def exercise_count(self, obj):
        """Contar ejercicios"""
        count = obj.exercises.count()
        return format_html(
            '<span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px;">{} ejercicio(s)</span>',
            count
        )
    exercise_count.short_description = 'Ejercicios'
    
    def rest_day_badge(self, obj):
        """Badge para días de descanso"""
        if obj.is_rest_day:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px;">DESCANSO</span>'
            )
        return "—"
    rest_day_badge.short_description = 'Descanso'


# ═════════════════════════════════════════════════════════════════════════════
# EXERCISE ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin para gestionar ejercicios"""
    
    list_display = (
        'name',
        'training_day_link',
        'sets_x_reps',
        'weight_display',
        'rest_display',
        'rpe_display',
        'completed_badge',
        'order',
    )
    
    list_filter = (
        'is_completed',
        'training_day__day_name',
        'rpe',
    )
    
    search_fields = (
        'name',
        'training_day__focus',
        'training_day__plan__name',
    )
    
    fieldsets = (
        ('📋 Información', {
            'fields': ('training_day', 'name', 'order')
        }),
        ('💪 Detalles del Ejercicio', {
            'fields': (
                ('sets', 'reps'),
                ('weight_kg', 'rest_seconds'),
                ('rpe',),
            )
        }),
        ('📝 Notas', {
            'fields': ('notes', 'video_url'),
            'classes': ('collapse',)
        }),
        ('✅ Estado', {
            'fields': ('is_completed',)
        }),
    )
    
    ordering = ('training_day', 'order')
    list_per_page = 100
    
    def training_day_link(self, obj):
        """Link al día de entrenamiento"""
        url = reverse('admin:plans_trainingday_change', args=[obj.training_day.id])
        return format_html('<a href="{}">{} ({})</a>', url, obj.training_day.day_name, obj.training_day.focus)
    training_day_link.short_description = 'Día'
    
    def sets_x_reps(self, obj):
        """Mostrar sets x reps"""
        return f"{obj.sets}×{obj.reps}"
    sets_x_reps.short_description = 'Sets × Reps'
    
    def weight_display(self, obj):
        """Mostrar peso"""
        if obj.weight_kg:
            return f"{obj.weight_kg} kg"
        return "—"
    weight_display.short_description = 'Peso'
    weight_display.admin_order_field = 'weight_kg'
    
    def rest_display(self, obj):
        """Mostrar descanso"""
        return f"{obj.rest_seconds}s"
    rest_display.short_description = 'Descanso'
    
    def rpe_display(self, obj):
        """Mostrar RPE con escala visual"""
        if obj.rpe:
            color = '#e74c3c' if obj.rpe >= 8 else '#f39c12' if obj.rpe >= 6 else '#27ae60'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}/10</span>',
                color, obj.rpe
            )
        return "—"
    rpe_display.short_description = 'RPE'
    
    def completed_badge(self, obj):
        """Badge de completado"""
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ HECHO</span>'
            )
        return "—"
    completed_badge.short_description = 'Estado'


# ═════════════════════════════════════════════════════════════════════════════
# MEAL ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    """Admin para gestionar comidas"""
    
    list_display = (
        'name',
        'meal_type_badge',
        'plan_link',
        'macro_display',
        'completed_badge',
        'order',
    )
    
    list_filter = (
        'meal_type',
        'is_completed',
        'plan__client',
    )
    
    search_fields = (
        'name',
        'plan__name',
        'plan__client__email',
    )
    
    fieldsets = (
        ('📋 Información', {
            'fields': ('plan', 'meal_type', 'name', 'order')
        }),
        ('🍎 Macronutrientes', {
            'fields': (
                ('calories',),
                ('protein_g', 'carbs_g', 'fat_g'),
            )
        }),
        ('📝 Descripción', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('✅ Estado', {
            'fields': ('is_completed',)
        }),
    )
    
    ordering = ('plan', 'order')
    list_per_page = 50
    
    def meal_type_badge(self, obj):
        """Badge de tipo de comida"""
        colors = {
            'breakfast': '#f39c12',
            'mid_morning': '#e67e22',
            'lunch': '#27ae60',
            'pre_workout': '#3498db',
            'post_workout': '#9b59b6',
            'dinner': '#34495e',
            'snack': '#95a5a6',
        }
        color = colors.get(obj.meal_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_meal_type_display()
        )
    meal_type_badge.short_description = 'Tipo'
    
    def plan_link(self, obj):
        """Link al plan"""
        url = reverse('admin:plans_plan_change', args=[obj.plan.id])
        return format_html('<a href="{}">{}</a>', url, obj.plan.name)
    plan_link.short_description = 'Plan'
    
    def macro_display(self, obj):
        """Mostrar macronutrientes de forma legible"""
        if all([obj.protein_g, obj.carbs_g, obj.fat_g]):
            return format_html(
                '🥩{}g 🍚{}g 🧈{}g',
                obj.protein_g, obj.carbs_g, obj.fat_g
            )
        return "—"
    macro_display.short_description = 'Macros'
    
    def completed_badge(self, obj):
        """Badge de completado"""
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ HECHO</span>'
            )
        return "—"
    completed_badge.short_description = 'Estado'