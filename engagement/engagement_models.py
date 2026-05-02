"""
engagement/chat/models.py  +  engagement/notifications/models.py
─────────────────────────────────────────────────────────────────
Chat entre coach y atleta, y sistema de notificaciones/alertas.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# ═══════════════════════════════════════════════════════════
#  CHAT — Mensajes entre coach y atleta
# ═══════════════════════════════════════════════════════════

class Conversation(models.Model):
    """
    Hilo de conversación entre dos usuarios (coach ↔ atleta).
    """
    coach   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_coach",
        limit_choices_to={"role": "coach"},
    )
    client  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_client",
        limit_choices_to={"role": "athlete"},
    )
    last_message_at  = models.DateTimeField(null=True, blank=True, db_index=True)
    unread_by_coach  = models.PositiveSmallIntegerField(default=0)
    unread_by_client = models.PositiveSmallIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "chat_conversation"
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        # Solo un hilo por par coach-cliente
        unique_together = ["coach", "client"]
        ordering = ["-last_message_at"]

    def __str__(self) -> str:
        return f"{self.coach.full_name} ↔ {self.client.full_name}"


class Message(models.Model):
    """
    Mensaje dentro de una conversación.
    """

    class MessageType(models.TextChoices):
        TEXT  = "text",  _("Texto")
        IMAGE = "image", _("Imagen")
        FILE  = "file",  _("Archivo")

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content      = models.TextField()
    message_type = models.CharField(max_length=6, choices=MessageType.choices, default=MessageType.TEXT)
    attachment   = models.FileField(upload_to="chat_attachments/", null=True, blank=True)
    is_read      = models.BooleanField(default=False, db_index=True)
    read_at      = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table   = "chat_message"
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self) -> str:
        return f"{self.sender.full_name}: {self.content[:60]}"


# ═══════════════════════════════════════════════════════════
#  NOTIFICATIONS — Alertas y recordatorios del sistema
# ═══════════════════════════════════════════════════════════

class Notification(models.Model):
    """
    Notificación interna del sistema para coach o atleta.
    Generada automáticamente por el AI Engine, cron jobs,
    o acciones del coach.
    """

    class NotifType(models.TextChoices):
        # Para coaches
        CLIENT_STAGNANT    = "client_stagnant",    _("Cliente estancado")
        LOW_COMPLIANCE     = "low_compliance",     _("Cumplimiento bajo")
        NO_DATA            = "no_data",            _("Sin registros")
        PLAN_EXPIRING      = "plan_expiring",      _("Plan por vencer")
        NEW_CLIENT         = "new_client",         _("Nuevo cliente")
        SESSION_REMINDER   = "session_reminder",   _("Recordatorio sesión")
        # Para atletas
        DAILY_REMINDER     = "daily_reminder",     _("Recordatorio diario")
        PLAN_UPDATED       = "plan_updated",       _("Plan actualizado")
        AI_SUGGESTION      = "ai_suggestion",      _("Sugerencia IA")
        MILESTONE_REACHED  = "milestone_reached",  _("Meta alcanzada")
        COACH_MESSAGE      = "coach_message",      _("Mensaje del coach")
        # Generales
        PAYMENT_DUE        = "payment_due",        _("Pago pendiente")
        SYSTEM             = "system",             _("Sistema")

    class Priority(models.TextChoices):
        LOW      = "low",      _("Baja")
        NORMAL   = "normal",   _("Normal")
        HIGH     = "high",     _("Alta")
        CRITICAL = "critical", _("Crítica")

    # ── Destinatario ─────────────────────────────────────────
    recipient    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    # ── Contenido ─────────────────────────────────────────────
    notif_type   = models.CharField(max_length=25, choices=NotifType.choices, db_index=True)
    priority     = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL, db_index=True)
    title        = models.CharField(max_length=200)
    body         = models.TextField()
    action_url   = models.CharField(max_length=200, blank=True, default="", help_text="URL relativa de acción.")
    extra_data   = models.JSONField(default=dict, help_text="Datos adicionales para el front-end.")

    # ── Estado ────────────────────────────────────────────────
    is_read      = models.BooleanField(default=False, db_index=True)
    read_at      = models.DateTimeField(null=True, blank=True)
    is_sent      = models.BooleanField(default=False, help_text="True si se envió por email/push.")

    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table   = "notifications_notification"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.priority}] {self.notif_type} → {self.recipient.full_name}"


class NotificationPreference(models.Model):
    """
    Preferencias de notificación por usuario.
    Permite desactivar tipos específicos.
    """
    user             = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notif_preferences",
    )
    email_enabled    = models.BooleanField(default=True)
    push_enabled     = models.BooleanField(default=True)
    daily_reminder   = models.BooleanField(default=True)
    reminder_time    = models.TimeField(default="08:00")
    weekly_report    = models.BooleanField(default=True)
    ai_suggestions   = models.BooleanField(default=True)
    coach_messages   = models.BooleanField(default=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table   = "notifications_preference"
        verbose_name = "Preferencias de Notificación"
        verbose_name_plural = "Preferencias de Notificación"

    def __str__(self) -> str:
        return f"Preferencias de {self.user.full_name}"
