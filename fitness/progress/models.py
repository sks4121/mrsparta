"""
fitness/progress/models.py
──────────────────────────
Registro semanal/diario del progreso del atleta.
Incluye peso, cumplimiento, medidas corporales y notas.
La IA usa esta tabla para detectar estancamientos.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgressLog(models.Model):
    """
    Registro de progreso por semana.
    Es la fuente principal de datos para el AI Engine.
    """

    # ── Relaciones ────────────────────────────────────────────
    client      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_logs",
        limit_choices_to={"role": "athlete"},
    )
    plan        = models.ForeignKey(
        "plans.Plan",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="progress_logs",
    )

    # ── Temporalidad ─────────────────────────────────────────
    date        = models.DateField(db_index=True)
    week_number = models.PositiveSmallIntegerField(default=1)

    # ── Métricas de peso y cuerpo ─────────────────────────────
    weight_kg         = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_pct      = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    muscle_mass_kg    = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_cm          = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    chest_cm          = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    hip_cm            = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    arm_cm            = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # ── Cumplimiento (0-100) ──────────────────────────────────
    training_compliance   = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="% de sesiones de entrenamiento completadas",
    )
    nutrition_compliance  = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="% de comidas del plan seguidas",
    )
    hydration_compliance  = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
    )

    # ── Energía y bienestar ───────────────────────────────────
    energy_level  = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    sleep_hours   = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    stress_level  = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    # ── Notas ─────────────────────────────────────────────────
    notes         = models.TextField(blank=True, default="")
    coach_notes   = models.TextField(blank=True, default="")

    # ── Flags del AI Engine ───────────────────────────────────
    is_stagnant      = models.BooleanField(default=False, db_index=True)
    ai_analyzed      = models.BooleanField(default=False)
    ai_alert_sent    = models.BooleanField(default=False)

    created_at    = models.DateTimeField(auto_now_add=True)

    @property
    def overall_compliance(self) -> int:
        """Promedio de los tres tipos de cumplimiento."""
        total = (
            self.training_compliance
            + self.nutrition_compliance
            + self.hydration_compliance
        )
        return total // 3

    class Meta:
        db_table   = "fitness_progresslog"
        verbose_name = "Registro de Progreso"
        verbose_name_plural = "Registros de Progreso"
        ordering = ["-date"]
        # Un atleta → un registro por día
        unique_together = ["client", "date"]
        indexes = [
            models.Index(fields=["client", "date"]),
            models.Index(fields=["is_stagnant"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.client.full_name} — Sem {self.week_number} "
            f"({self.date}) · {self.weight_kg}kg"
        )


class WorkoutSession(models.Model):
    """
    Registro de una sesión de entrenamiento individual completada.
    Se crea cada vez que el atleta marca un TrainingDay como completado.
    """

    class Status(models.TextChoices):
        COMPLETED = "completed", _("Completado")
        PARTIAL   = "partial",   _("Parcial")
        SKIPPED   = "skipped",   _("Saltado")

    client       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_sessions",
    )
    training_day = models.ForeignKey(
        "plans.TrainingDay",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sessions",
    )
    date         = models.DateField()
    status       = models.CharField(max_length=12, choices=Status.choices, default=Status.COMPLETED)
    duration_min = models.PositiveSmallIntegerField(null=True, blank=True)
    rpe_avg      = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    notes        = models.TextField(blank=True, default="")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "fitness_workoutsession"
        verbose_name = "Sesión de Entrenamiento"
        verbose_name_plural = "Sesiones de Entrenamiento"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.client.full_name} — {self.date} [{self.status}]"
