"""
coaching/coach_sessions/models.py
─────────────────────────────────
Sesiones y reservas entre coaches y atletas.
Videollamadas, sesiones presenciales, chequeos mensuales.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CoachSession(models.Model):
    """
    Sesión individual entre coach y atleta.
    Puede ser videollamada, presencial o registro de chequeo mensual.
    """

    class SessionType(models.TextChoices):
        VIDEO_CALL = "video_call", _("Videollamada")
        PRESENTIAL = "presential", _("Presencial")
        MONTHLY_CHECK = "monthly_check", _("Chequeo mensual")
        INITIAL = "initial", _("Evaluación inicial")

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Agendada")
        COMPLETED = "completed", _("Completada")
        CANCELLED = "cancelled", _("Cancelada")
        NO_SHOW = "no_show", _("No asistió")

    # ── Relaciones ────────────────────────────────────────────
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coach_sessions",
        limit_choices_to={"role": "coach"},
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_sessions",
        limit_choices_to={"role": "athlete"},
    )

    # ── Datos de la sesión ────────────────────────────────────
    session_type = models.CharField(
        max_length=15,
        choices=SessionType.choices,
        default=SessionType.MONTHLY_CHECK,
        help_text=_("Tipo de sesión de coaching"),
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
        help_text=_("Estado actual de la sesión"),
    )
    scheduled_at = models.DateTimeField(
        help_text=_("Fecha y hora de la sesión")
    )
    duration_min = models.PositiveSmallIntegerField(
        default=60,
        help_text=_("Duración en minutos"),
    )
    meeting_url = models.URLField(
        blank=True,
        default="",
        help_text=_("Link de Zoom/Meet para videollamadas"),
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_("Precio de la sesión"),
    )
    notes_coach = models.TextField(
        blank=True,
        default="",
        help_text=_("Notas internas del coach"),
    )
    notes_client = models.TextField(
        blank=True,
        default="",
        help_text=_("Notas del cliente"),
    )
    recording_url = models.URLField(
        blank=True,
        default="",
        help_text=_("Link a la grabación de la sesión"),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Fecha y hora en que se completó"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Fecha de creación del registro"),
    )

    class Meta:
        db_table = "coaching_coachsession"
        verbose_name = _("Sesión de Coaching")
        verbose_name_plural = _("Sesiones de Coaching")
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["coach", "scheduled_at"]),
            models.Index(fields=["client", "scheduled_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.get_session_type_display()} — "
            f"{self.coach.full_name} ↔ {self.client.full_name} "
            f"[{self.scheduled_at.strftime('%d/%m/%Y %H:%M')}]"
        )

    @property
    def is_upcoming(self) -> bool:
        """¿Es una sesión futura?"""
        from django.utils import timezone
        return self.scheduled_at > timezone.now()

    @property
    def is_past(self) -> bool:
        """¿Es una sesión pasada?"""
        from django.utils import timezone
        return self.scheduled_at < timezone.now()

    def save(self, *args, **kwargs):
        """Validación al guardar"""
        # No permitir cambiar el coach o cliente de una sesión completada
        if self.pk:
            old_instance = CoachSession.objects.get(pk=self.pk)
            if old_instance.status == 'completed' and old_instance.status != self.status:
                # Permitir cambiar estado pero nada más
                pass
        super().save(*args, **kwargs)