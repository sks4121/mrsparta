"""
core/billing/admin.py
─────────────────────
Administración de planes, suscripciones y pagos (Stripe).
Gestión del billing y ingresos de coaches.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Plan, Subscription, Payment


# ═════════════════════════════════════════════════════════════════════════════
# PLAN ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin para gestionar planes del sistema"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'name',
        'tier_badge',
        'price_display',
        'max_clients_display',
        'features_display',
        'stripe_badge',
        'is_active_badge',
        'subscriber_count',
    )
    
    list_filter = (
        'tier',
        'is_active',
        'has_ai',
        'has_human_coach',
        'has_video_call',
    )
    
    search_fields = ('name', 'stripe_price_id')
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información Básica
        ('📋 Información Básica', {
            'fields': ('name', 'tier', 'description')
        }),
        
        # Precios
        ('💰 Precios', {
            'fields': (
                'price_monthly',
                'max_clients',
            )
        }),
        
        # Características
        ('✨ Características', {
            'fields': (
                'has_ai',
                'has_human_coach',
                'has_video_call',
            ),
            'description': 'Marca las características incluidas en este plan.'
        }),
        
        # Stripe
        ('🔐 Stripe', {
            'fields': ('stripe_price_id',),
            'classes': ('collapse',),
            'description': 'ID del precio en Stripe (ej: price_1Abc...)'
        }),
        
        # Estado
        ('⏳ Estado', {
            'fields': ('is_active',)
        }),
        
        # Timestamps
        ('📅 Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    ordering = ('price_monthly',)
    list_per_page = 50
    
    # ── Métodos para el listado ────────────────────────────────
    def tier_badge(self, obj):
        """Badge del tier"""
        colors = {
            'basic': '#3498db',
            'premium': '#f39c12',
            'elite': '#e74c3c',
        }
        color = colors.get(obj.tier, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_tier_display()
        )
    tier_badge.short_description = 'Tier'
    tier_badge.admin_order_field = 'tier'
    
    def price_display(self, obj):
        """Mostrar precio"""
        return f"${obj.price_monthly}/mes"
    price_display.short_description = 'Precio'
    price_display.admin_order_field = 'price_monthly'
    
    def max_clients_display(self, obj):
        """Mostrar máximo de clientes"""
        return format_html(
            '<span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px;">👥 {} clientes</span>',
            obj.max_clients
        )
    max_clients_display.short_description = 'Max Clientes'
    max_clients_display.admin_order_field = 'max_clients'
    
    def features_display(self, obj):
        """Mostrar features incluidos"""
        features = []
        if obj.has_ai:
            features.append('🤖 IA')
        if obj.has_human_coach:
            features.append('👨‍🏫 Coach')
        if obj.has_video_call:
            features.append('📹 Video')
        
        if features:
            return format_html(' {} ', ' '.join(features))
        return "—"
    features_display.short_description = 'Características'
    
    def stripe_badge(self, obj):
        """Mostrar estado de Stripe"""
        if obj.stripe_price_id:
            return format_html(
                '<span style="background-color: #5469d4; color: white; padding: 3px 8px; border-radius: 3px;">✓ Conectado</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px;">✗ No vinculado</span>'
        )
    stripe_badge.short_description = 'Stripe'
    
    def is_active_badge(self, obj):
        """Badge de estado activo"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 3px;">✓ Activo</span>'
            )
        return format_html(
            '<span style="background-color: #95a5a6; color: white; padding: 3px 8px; border-radius: 3px;">✗ Inactivo</span>'
        )
    is_active_badge.short_description = 'Estado'
    
    def subscriber_count(self, obj):
        """Contar suscriptores activos"""
        count = obj.subscriptions.filter(status__in=['active', 'trialing']).count()
        return format_html(
            '<span style="background-color: #9b59b6; color: white; padding: 3px 8px; border-radius: 3px;">{} suscriptores</span>',
            count
        )
    subscriber_count.short_description = 'Suscriptores'


# ═════════════════════════════════════════════════════════════════════════════
# PAYMENT INLINE
# ═════════════════════════════════════════════════════════════════════════════

class PaymentInline(admin.TabularInline):
    """Inline para ver pagos dentro de una suscripción"""
    model = Payment
    extra = 0
    fields = ('stripe_payment_id', 'amount', 'currency', 'status', 'paid_at')
    readonly_fields = ('stripe_payment_id', 'paid_at', 'created_at')
    ordering = ('-created_at',)


# ═════════════════════════════════════════════════════════════════════════════
# SUBSCRIPTION ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin para gestionar suscripciones de coaches"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'coach_email',
        'plan_display',
        'status_badge',
        'active_clients_display',
        'monthly_revenue_display',
        'trial_status',
        'period_dates',
    )
    
    list_filter = (
        'status',
        'plan__tier',
        'plan',
        ('trial_end', admin.RelatedOnlyFieldListFilter),
    )
    
    search_fields = (
        'coach__email',
        'coach__first_name',
        'coach__last_name',
        'stripe_sub_id',
        'stripe_customer_id',
    )
    
    inlines = [PaymentInline]
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información General
        ('👥 Coach y Plan', {
            'fields': ('coach', 'plan')
        }),
        
        # Estado
        ('📊 Estado', {
            'fields': (
                'status',
                ('active_clients', 'monthly_revenue'),
            )
        }),
        
        # Periodo de Suscripción
        ('📅 Período de Suscripción', {
            'fields': (
                ('current_period_start', 'current_period_end'),
                'trial_end',
            )
        }),
        
        # Stripe
        ('🔐 Stripe', {
            'fields': (
                'stripe_sub_id',
                'stripe_customer_id',
            ),
            'classes': ('collapse',),
            'description': 'IDs de Stripe (automáticamente sincronizados)'
        }),
        
        # Timestamps
        ('📅 Timestamps', {
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
        'stripe_sub_id',
        'stripe_customer_id',
    )
    
    ordering = ('-created_at',)
    list_per_page = 25
    
    # ── Acciones ───────────────────────────────────────────────
    actions = ['mark_active', 'mark_canceled', 'mark_past_due']
    
    # ── Métodos para el listado ────────────────────────────────
    def coach_email(self, obj):
        """Link al coach"""
        url = reverse('admin:users_user_change', args=[obj.coach.id])
        return format_html('<a href="{}">{}</a>', url, obj.coach.email)
    coach_email.short_description = 'Coach'
    coach_email.admin_order_field = 'coach__email'
    
    def plan_display(self, obj):
        """Mostrar plan con precio"""
        url = reverse('admin:billing_plan_change', args=[obj.plan.id])
        return format_html(
            '<a href="{}">{} (${}/mes)</a>',
            url, obj.plan.name, obj.plan.price_monthly
        )
    plan_display.short_description = 'Plan'
    plan_display.admin_order_field = 'plan__name'
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        colors = {
            'active': '#27ae60',
            'past_due': '#f39c12',
            'canceled': '#e74c3c',
            'trialing': '#3498db',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def active_clients_display(self, obj):
        """Mostrar clientes activos vs máximo"""
        max_clients = obj.plan.max_clients
        percent = int((obj.active_clients / max_clients * 100)) if max_clients > 0 else 0
        
        color = '#27ae60' if percent < 80 else '#f39c12' if percent < 100 else '#e74c3c'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}/{} ({}%)</span>',
            color, obj.active_clients, max_clients, percent
        )
    active_clients_display.short_description = 'Clientes'
    active_clients_display.admin_order_field = 'active_clients'
    
    def monthly_revenue_display(self, obj):
        """Mostrar ingresos mensuales"""
        return f"${obj.monthly_revenue}"
    monthly_revenue_display.short_description = 'Ingresos'
    monthly_revenue_display.admin_order_field = 'monthly_revenue'
    
    def trial_status(self, obj):
        """Mostrar estado de prueba"""
        if obj.trial_end:
            if timezone.now() < obj.trial_end:
                days_left = (obj.trial_end - timezone.now()).days
                return format_html(
                    '<span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px;">Prueba ({} días)</span>',
                    days_left
                )
            else:
                return format_html(
                    '<span style="background-color: #95a5a6; color: white; padding: 3px 8px; border-radius: 3px;">Prueba expirada</span>'
                )
        return "—"
    trial_status.short_description = 'Prueba'
    
    def period_dates(self, obj):
        """Mostrar período actual"""
        if obj.current_period_start and obj.current_period_end:
            return f"{obj.current_period_start.strftime('%d/%m')} - {obj.current_period_end.strftime('%d/%m')}"
        return "—"
    period_dates.short_description = 'Período'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_active(self, request, queryset):
        """Marcar como activa"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} suscripción(es) marcada(s) como activa.')
    mark_active.short_description = '✓ Marcar como Activa'
    
    def mark_canceled(self, request, queryset):
        """Marcar como cancelada"""
        updated = queryset.update(status='canceled')
        self.message_user(request, f'{updated} suscripción(es) cancelada(s).')
    mark_canceled.short_description = '✗ Marcar como Cancelada'
    
    def mark_past_due(self, request, queryset):
        """Marcar como vencida"""
        updated = queryset.update(status='past_due')
        self.message_user(request, f'{updated} suscripción(es) con pago vencido.')
    mark_past_due.short_description = '⚠️ Marcar como Pago Vencido'


# ═════════════════════════════════════════════════════════════════════════════
# PAYMENT ADMIN
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para gestionar pagos y transacciones"""
    
    # ── Listado principal ──────────────────────────────────────
    list_display = (
        'coach_email',
        'amount_display',
        'status_badge',
        'subscription_plan',
        'paid_at',
        'stripe_badge',
    )
    
    list_filter = (
        'status',
        'currency',
        ('paid_at', admin.DateFieldListFilter),
        'created_at',
    )
    
    search_fields = (
        'subscription__coach__email',
        'stripe_payment_id',
        'subscription__coach__first_name',
        'subscription__coach__last_name',
    )
    
    # ── Formulario ─────────────────────────────────────────────
    fieldsets = (
        # Información
        ('📋 Información del Pago', {
            'fields': (
                'subscription',
                ('amount', 'currency'),
                'status',
            )
        }),
        
        # Stripe
        ('🔐 Stripe', {
            'fields': ('stripe_payment_id',),
            'classes': ('collapse',)
        }),
        
        # Fechas
        ('📅 Fechas', {
            'fields': (
                'paid_at',
                'created_at',
            )
        }),
    )
    
    readonly_fields = (
        'created_at',
        'stripe_payment_id',
    )
    
    ordering = ('-created_at',)
    list_per_page = 50
    
    # ── Acciones ───────────────────────────────────────────────
    actions = ['mark_succeeded', 'mark_failed']
    
    # ── Métodos para el listado ────────────────────────────────
    def coach_email(self, obj):
        """Link al coach"""
        url = reverse('admin:users_user_change', args=[obj.subscription.coach.id])
        return format_html('<a href="{}">{}</a>', url, obj.subscription.coach.email)
    coach_email.short_description = 'Coach'
    coach_email.admin_order_field = 'subscription__coach__email'
    
    def amount_display(self, obj):
        """Mostrar monto"""
        color = '#27ae60' if obj.status == 'succeeded' else '#e74c3c' if obj.status == 'failed' else '#f39c12'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${} {}</span>',
            color, obj.amount, obj.currency.upper()
        )
    amount_display.short_description = 'Monto'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        """Badge de estado"""
        colors = {
            'succeeded': '#27ae60',
            'pending': '#f39c12',
            'failed': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def subscription_plan(self, obj):
        """Mostrar plan de la suscripción"""
        url = reverse('admin:billing_subscription_change', args=[obj.subscription.id])
        return format_html('<a href="{}">{}</a>', url, obj.subscription.plan.name)
    subscription_plan.short_description = 'Plan'
    
    def stripe_badge(self, obj):
        """Badge de Stripe"""
        if obj.stripe_payment_id:
            return format_html(
                '<span style="background-color: #5469d4; color: white; padding: 3px 8px; border-radius: 3px;">✓</span>'
            )
        return "—"
    stripe_badge.short_description = 'Stripe'
    
    # ── Acciones personalizadas ────────────────────────────────
    def mark_succeeded(self, request, queryset):
        """Marcar como exitoso"""
        updated = queryset.update(status='succeeded')
        self.message_user(request, f'{updated} pago(s) marcado(s) como exitoso.')
    mark_succeeded.short_description = '✓ Marcar como Exitoso'
    
    def mark_failed(self, request, queryset):
        """Marcar como fallido"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} pago(s) marcado(s) como fallido.')
    mark_failed.short_description = '✗ Marcar como Fallido'