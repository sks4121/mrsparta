"""
ai_engine/models.py
───────────────────
Núcleo de IA: análisis de progreso, sugerencias automáticas
y registro de cada decisión que toma el sistema.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# ═══════════════════════════════════════════════════════════
#  AI ENGINE — Análisis y sugerencias
# ═══════════════════════════════════════════════════════════

class AIAnalysis(models.Model):
    """
    Resultado de un análisis del AI Engine sobre un atleta.
    Se genera automáticamente (cron / señal post-save en ProgressLog).
    """

    class Status(models.TextChoices):
        PENDING  = "pending",  _("Pendiente")
        DONE     = "done",     _("Completado")
        FAILED   = "failed",   _("Error")

    client      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_analyses",
    )
    progress_log = models.OneToOneField(
        "progress.ProgressLog",
        on_delete=models.CASCADE,
        related_name="ai_analysis",
        null=True, blank=True,
    )
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    # ── Resultado del análisis ────────────────────────────────
    summary      = models.TextField(blank=True, default="")
    stagnation_detected  = models.BooleanField(default=False)
    low_compliance       = models.BooleanField(default=False)
    alert_level  = models.CharField(
        max_length=10,
        choices=[("none","Ninguno"),("warn","Advertencia"),("critical","Crítico")],
        default="none",
        db_index=True,
    )

    # ── Raw data ──────────────────────────────────────────────
    context_data  = models.JSONField(
        default=dict,
        help_text="Snapshot del contexto enviado al modelo de IA.",
    )
    raw_response  = models.TextField(blank=True, default="")

    analyzed_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "ai_aianalysis"
        verbose_name = "Análisis IA"
        verbose_name_plural = "Análisis IA"
        ordering = ["-analyzed_at"]

    def __str__(self) -> str:
        return f"Análisis {self.client.full_name} — {self.analyzed_at.date()} [{self.alert_level}]"


class AISuggestion(models.Model):
    """
    Sugerencia concreta generada por la IA para un atleta.
    Puede ser aprobada o rechazada por el coach.
    """

    class SuggestionType(models.TextChoices):
        INCREASE_CALORIES  = "increase_calories",  _("Aumentar calorías")
        DECREASE_CALORIES  = "decrease_calories",  _("Reducir calorías")
        INCREASE_VOLUME    = "increase_volume",    _("Aumentar volumen")
        DECREASE_VOLUME    = "decrease_volume",    _("Reducir volumen")
        INCREASE_LOAD      = "increase_load",      _("Aumentar carga")
        ADD_REST_DAY       = "add_rest_day",       _("Agregar día de descanso")
        CONTACT_CLIENT     = "contact_client",     _("Contactar al atleta")
        RENEW_PLAN         = "renew_plan",         _("Renovar plan")
        OTHER              = "other",              _("Otro")

    class ApprovalStatus(models.TextChoices):
        PENDING  = "pending",  _("Pendiente")
        APPROVED = "approved", _("Aprobada")
        REJECTED = "rejected", _("Rechazada")
        APPLIED  = "applied",  _("Aplicada")

    analysis     = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE, related_name="suggestions")
    client       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_suggestions")
    coach        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="pending_suggestions",
    )

    suggestion_type = models.CharField(max_length=25, choices=SuggestionType.choices)
    description     = models.TextField()
    value_change    = models.JSONField(
        default=dict,
        help_text='Ej: {"calories": 200} o {"volume_pct": -10}',
    )
    approval_status = models.CharField(max_length=10, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING, db_index=True)
    approved_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_suggestions",
    )
    applied_at      = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "ai_aisuggestion"
        verbose_name = "Sugerencia IA"
        verbose_name_plural = "Sugerencias IA"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.suggestion_type} → {self.client.full_name} [{self.approval_status}]"


# ═══════════════════════════════════════════════════════════
#  AI RULES — Reglas de decisión del sistema
# ═══════════════════════════════════════════════════════════

class AIRule(models.Model):
    """
    Reglas de negocio que definen el comportamiento del AI Engine.
    Configuradas por Admin. El Engine las evalúa en cada análisis.

    Ejemplo:
        name      = "stagnation_calories"
        condition = {"weight_change_days": 14, "operator": "lte", "value": 0}
        action    = {"type": "increase_calories", "value": 200}
    """

    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    condition   = models.JSONField(
        help_text='Ej: {"metric": "weight_change", "days": 14, "operator": "lte", "value": 0}',
    )
    action      = models.JSONField(
        help_text='Ej: {"type": "increase_calories", "delta": 200}',
    )
    priority    = models.PositiveSmallIntegerField(default=10)
    is_active   = models.BooleanField(default=True, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table   = "ai_airule"
        verbose_name = "Regla IA"
        verbose_name_plural = "Reglas IA"
        ordering = ["priority"]

    def __str__(self) -> str:
        return f"[{self.priority}] {self.name} ({'activa' if self.is_active else 'inactiva'})"


# ═══════════════════════════════════════════════════════════
#  AI INSIGHTS — Chat / respuestas contextuales
# ═══════════════════════════════════════════════════════════

class AIInsight(models.Model):
    """
    Insight generado por el Spartan AI para un atleta o coach.
    Puede ser una respuesta de chat o un insight proactivo.
    """

    class InsightType(models.TextChoices):
        CHAT_RESPONSE = "chat",      _("Respuesta de Chat")
        WEEKLY_REPORT = "weekly",    _("Reporte Semanal")
        ALERT         = "alert",     _("Alerta Proactiva")
        MILESTONE     = "milestone", _("Logro Alcanzado")

    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_insights")
    insight_type = models.CharField(max_length=12, choices=InsightType.choices, default=InsightType.CHAT_RESPONSE)
    title        = models.CharField(max_length=200, blank=True, default="")
    content      = models.TextField()
    context_data = models.JSONField(default=dict)
    is_read      = models.BooleanField(default=False, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table   = "ai_aiinsight"
        verbose_name = "Insight IA"
        verbose_name_plural = "Insights IA"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.insight_type} → {self.user.full_name}"


class AIChatMessage(models.Model):
    """
    Historial de mensajes del Spartan AI Chat.
    """

    class Role(models.TextChoices):
        USER      = "user",      _("Usuario")
        ASSISTANT = "assistant", _("Spartan AI")
        SYSTEM    = "system",    _("Sistema")

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_chat_messages")
    role        = models.CharField(max_length=10, choices=Role.choices)
    content     = models.TextField()
    context_snapshot = models.JSONField(
        default=dict,
        help_text="Snapshot del perfil y progreso del usuario en este momento.",
    )
    tokens_used = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "ai_aichatmessage"
        verbose_name = "Mensaje Chat IA"
        verbose_name_plural = "Mensajes Chat IA"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"[{self.role}] {self.user.full_name} — {self.created_at.date()}"
