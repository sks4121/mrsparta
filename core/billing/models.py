"""
core/billing/models.py
──────────────────────
Gestión de suscripciones y pagos (Stripe).
Cada Coach tiene una suscripción que controla cuántos atletas puede gestionar.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    """
    Definición de planes del sistema (Basic, Premium, Elite).
    Creados por Admin, no por usuarios.
    """

    class Tier(models.TextChoices):
        BASIC   = "basic",   _("Basic")
        PREMIUM = "premium", _("Premium")
        ELITE   = "elite",   _("Elite")

    name            = models.CharField(max_length=50, unique=True)
    tier            = models.CharField(max_length=10, choices=Tier.choices, unique=True)
    price_monthly   = models.DecimalField(max_digits=8, decimal_places=2)
    max_clients     = models.PositiveIntegerField(
        default=10,
        help_text="Máximo de clientes activos permitidos.",
    )
    has_ai          = models.BooleanField(default=True)
    has_human_coach = models.BooleanField(default=False)
    has_video_call  = models.BooleanField(default=False)
    description     = models.TextField(blank=True, default="")
    stripe_price_id = models.CharField(max_length=100, blank=True, default="")
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "billing_plan"
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["price_monthly"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price_monthly}/mes)"


class Subscription(models.Model):
    """
    Suscripción activa de un Coach.
    Un Coach → Una suscripción activa a la vez.
    """

    class Status(models.TextChoices):
        ACTIVE    = "active",    _("Activa")
        PAST_DUE  = "past_due",  _("Pago vencido")
        CANCELED  = "canceled",  _("Cancelada")
        TRIALING  = "trialing",  _("En prueba")

    coach            = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
        limit_choices_to={"role": "coach"},
    )
    plan             = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIALING, db_index=True)
    stripe_sub_id    = models.CharField(max_length=100, blank=True, default="", unique=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, default="")
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end   = models.DateTimeField(null=True, blank=True)
    trial_end        = models.DateTimeField(null=True, blank=True)
    active_clients   = models.PositiveIntegerField(default=0)
    monthly_revenue  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    @property
    def is_active(self) -> bool:
        return self.status in (self.Status.ACTIVE, self.Status.TRIALING)

    class Meta:
        db_table   = "billing_subscription"
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self) -> str:
        return f"{self.coach.full_name} → {self.plan.name} [{self.status}]"


class Payment(models.Model):
    """
    Registro de cada pago procesado (webhook de Stripe).
    """

    class Status(models.TextChoices):
        SUCCEEDED = "succeeded", _("Exitoso")
        PENDING   = "pending",   _("Pendiente")
        FAILED    = "failed",    _("Fallido")

    subscription     = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount           = models.DecimalField(max_digits=8, decimal_places=2)
    currency         = models.CharField(max_length=3, default="usd")
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stripe_payment_id = models.CharField(max_length=100, blank=True, default="", unique=True)
    paid_at          = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "billing_payment"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"${self.amount} [{self.status}] — {self.subscription.coach.full_name}"
