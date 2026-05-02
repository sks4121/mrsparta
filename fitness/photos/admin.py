"""
fitness/photos/admin.py
───────────────────────
Administración de fotos de progreso.
Galería y seguimiento visual del progreso del atleta.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import ProgressPhoto


@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(admin.ModelAdmin):
    """Admin para gestionar fotos de progreso"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'photo_thumbnail',
        'client_email',
        'week_display',
        'angle_badge',
        'taken_at',
        'comparison_badge',
        'visibility_badge',
        'uploaded_at',
    )
    
    list_filter = (
        'angle',
        'week_number',
        'is_comparison',
        'visible_to_coach',
        'taken_at',
        'uploaded_at',
    )
    
    search_fields = (
        'client__email',
        'client__first_name',
        'client__last_name',
        'notes',
    )
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información General
        ('📸 Información General', {
            'fields': ('client', 'progress_log', 'week_number')
        }),
        
        # Imagen
        ('🖼️ Imagen', {
            'fields': (
                'image',
                'image_url',
                'thumbnail_url',
                'image_preview',
            )
        }),
        
        # Metadatos
        ('📋 Metadatos', {
            'fields': (
                'angle',
                'taken_at',
                'notes',
            )
        }),
        
        # Configuración de Visibilidad
        ('🔒 Visibilidad', {
            'fields': (
                'visible_to_coach',
                'is_comparison',
            )
        }),
        
        # Timestamps (Solo lectura)
        ('⏰ Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'uploaded_at',
        'image_url',
        'image_preview',
    )
    
    ordering = ('-uploaded_at',)
    list_per_page = 25
    
    # ── Acciones personalizadas ────────────────────────────────
    actions = [
        'mark_as_comparison',
        'unmark_as_comparison',
        'visible_to_coach_on',
        'visible_to_coach_off',
    ]
    
    # ── Métodos para el listado ────────────────────────────────
    def photo_thumbnail(self, obj):
        """Mostrar miniatura de la foto"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 3px;" />',
                obj.image.url
            )
        return "—"
    photo_thumbnail.short_description = 'Foto'
    
    def client_email(self, obj):
        """Mostrar email del cliente"""
        url = reverse('admin:users_user_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.email)
    client_email.short_description = 'Cliente'
    client_email.admin_order_field = 'client__email'
    
    def week_display(self, obj):
        """Mostrar semana formateada"""
        return f"Semana {obj.week_number}"
    week_display.short_description = 'Semana'
    week_display.admin_order_field = 'week_number'
    
    def angle_badge(self, obj):
        """Badge del ángulo de la foto"""
        angles_display = {
            'front': ('Frente', '#3498db'),
            'back': ('Espalda', '#e74c3c'),
            'side_l': ('Izq', '#9b59b6'),
            'side_r': ('Der', '#2ecc71'),
            'other': ('Otro', '#95a5a6'),
        }
        
        display_name, color = angles_display.get(obj.angle, ('?', '#95a5a6'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, display_name
        )
    angle_badge.short_description = 'Ángulo'
    angle_badge.admin_order_field = 'angle'
    
    def comparison_badge(self, obj):
        """Badge para marcar foto de comparación"""
        if obj.is_comparison:
            return format_html(
                '<span style="background-color: #f39c12; color: white; padding: 3px 8px; border-radius: 3px;">⭐ COMPARACIÓN</span>'
            )
        return "—"
    comparison_badge.short_description = 'Comparación'
    comparison_badge.admin_order_field = 'is_comparison'
    
    def visibility_badge(self, obj):
        """Badge de visibilidad al coach"""
        if obj.visible_to_coach:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">👁️ Visible</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px;">🚫 Oculta</span>'
        )
    visibility_badge.short_description = 'Coach'
    visibility_badge.admin_order_field = 'visible_to_coach'
    
    def image_preview(self, obj):
        """Preview de la imagen en el formulario"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 400px; border-radius: 5px;" />',
                obj.image.url
            )
        return "No hay imagen"
    image_preview.short_description = 'Preview'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_as_comparison(self, request, queryset):
        """Marcar fotos como comparación"""
        updated = queryset.update(is_comparison=True)
        self.message_user(request, f'{updated} foto(s) marcada(s) como comparación.')
    mark_as_comparison.short_description = '⭐ Marcar como comparación'
    
    def unmark_as_comparison(self, request, queryset):
        """Desmarcar fotos de comparación"""
        updated = queryset.update(is_comparison=False)
        self.message_user(request, f'{updated} foto(s) desmarcada(s) de comparación.')
    unmark_as_comparison.short_description = '⭕ Desmarcar de comparación'
    
    def visible_to_coach_on(self, request, queryset):
        """Hacer visibles al coach"""
        updated = queryset.update(visible_to_coach=True)
        self.message_user(request, f'{updated} foto(s) ahora visible(s) al coach.')
    visible_to_coach_on.short_description = '👁️ Hacer visibles al coach'
    
    def visible_to_coach_off(self, request, queryset):
        """Ocultar del coach"""
        updated = queryset.update(visible_to_coach=False)
        self.message_user(request, f'{updated} foto(s) ahora oculta(s) al coach.')
    visible_to_coach_off.short_description = '🚫 Ocultar al coach'
    
    # ── Personalización adicional ──────────────────────────────
    def get_readonly_fields(self, request, obj=None):
        """Si es edición, hacer readonly la imagen"""
        if obj:
            return self.readonly_fields + ['image']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Hook al guardar el modelo"""
        super().save_model(request, obj, form, change)
        # La URL se auto-completa en el método save() del modelo
    
    # ── Filtros personalizados ─────────────────────────────────
    class ClientFilter(admin.SimpleListFilter):
        """Filtro por cliente con conteo de fotos"""
        title = 'Cliente'
        parameter_name = 'client'
        
        def lookups(self, request, model_admin):
            clients = (
                ProgressPhoto.objects
                .values('client__email')
                .annotate(count=Count('id'))
                .order_by('client__email')
            )
            return [
                (client['client__email'], f"{client['client__email']} ({client['count']})")
                for client in clients
            ]
        
        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(client__email=self.value())
            return queryset