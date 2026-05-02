"""
fitness/plans/models.py
───────────────────────
Planes de entrenamiento y nutrición asignados a atletas.
Cada plan tiene semanas → días → ejercicios (entrenamiento)
o comidas → ítems (nutrición).
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class Plan(models.Model):
    """Plan maestro: puede ser de entrenamiento, nutrición o ambos."""

    class PlanType(models.TextChoices):
        TRAINING   = "training",   _("Entrenamiento")
        NUTRITION  = "nutrition",  _("Nutrición")
        COMBINED   = "combined",   _("Combinado")

    class Status(models.TextChoices):
        DRAFT   = "draft",   _("Borrador")
        ACTIVE  = "active",  _("Activo")
        PAUSED  = "paused",  _("Pausado")
        DONE    = "done",    _("Completado")

    class CreatedBy(models.TextChoices):
        COACH = "coach", _("Coach")
        AI    = "ai",    _("IA")
        BOTH  = "both",  _("IA + Coach")

    # ── Relaciones ────────────────────────────────────────────
    client     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plans",
        limit_choices_to={"role": "athlete"},
    )
    coach      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_plans",
        limit_choices_to={"role": "coach"},
    )

    # ── Metadatos ─────────────────────────────────────────────
    name         = models.CharField(max_length=120)
    plan_type    = models.CharField(max_length=10, choices=PlanType.choices, default=PlanType.COMBINED)
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by   = models.CharField(max_length=10, choices=CreatedBy.choices, default=CreatedBy.AI)
    description  = models.TextField(blank=True, default="")
    goals_notes  = models.TextField(blank=True, default="")

    # ── Temporalidad ─────────────────────────────────────────
    week_number   = models.PositiveSmallIntegerField(default=1)
    total_weeks   = models.PositiveSmallIntegerField(default=12)
    start_date    = models.DateField(null=True, blank=True)
    end_date      = models.DateField(null=True, blank=True)

    # ── Nutrición (resumen) ───────────────────────────────────
    daily_calories  = models.PositiveIntegerField(null=True, blank=True)
    protein_g       = models.PositiveSmallIntegerField(null=True, blank=True)
    carbs_g         = models.PositiveSmallIntegerField(null=True, blank=True)
    fat_g           = models.PositiveSmallIntegerField(null=True, blank=True)
    water_liters    = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table   = "fitness_plan"
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.client.full_name} [Sem {self.week_number}/{self.total_weeks}]"


class TrainingDay(models.Model):
    """Un día de entrenamiento dentro de un plan."""

    class DayName(models.TextChoices):
        MON = "monday",    _("Lunes")
        TUE = "tuesday",   _("Martes")
        WED = "wednesday", _("Miércoles")
        THU = "thursday",  _("Jueves")
        FRI = "friday",    _("Viernes")
        SAT = "saturday",  _("Sábado")
        SUN = "sunday",    _("Domingo")

    plan        = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="training_days")
    day_name    = models.CharField(max_length=12, choices=DayName.choices)
    focus       = models.CharField(max_length=120, blank=True, default="", help_text="Ej: Pecho + Tríceps")
    is_rest_day = models.BooleanField(default=False)
    order       = models.PositiveSmallIntegerField(default=1)
    notes       = models.TextField(blank=True, default="")

    class Meta:
        db_table   = "fitness_trainingday"
        verbose_name = "Día de Entrenamiento"
        verbose_name_plural = "Días de Entrenamiento"
        ordering = ["order"]
        unique_together = ["plan", "day_name"]

    def __str__(self) -> str:
        return f"{self.day_name} — {self.focus or 'Descanso'}"


class Exercise(models.Model):
    """Ejercicio individual dentro de un TrainingDay."""

    training_day  = models.ForeignKey(TrainingDay, on_delete=models.CASCADE, related_name="exercises")
    name          = models.CharField(max_length=120)
    sets          = models.PositiveSmallIntegerField(default=3)
    reps          = models.CharField(max_length=20, default="10", help_text="Ej: '8-12' o '15'")
    weight_kg     = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rest_seconds  = models.PositiveSmallIntegerField(default=90)
    rpe           = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating of Perceived Exertion (1-10)",
    )
    notes         = models.TextField(blank=True, default="")
    video_url     = models.URLField(blank=True, default="")
    order         = models.PositiveSmallIntegerField(default=1)
    is_completed  = models.BooleanField(default=False)

    class Meta:
        db_table   = "fitness_exercise"
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.name} — {self.sets}×{self.reps}"


class Meal(models.Model):
    """Comida del día dentro de un plan de nutrición."""

    class MealType(models.TextChoices):
        BREAKFAST  = "breakfast",  _("Desayuno")
        MID_MORNING= "mid_morning",_("Media Mañana")
        LUNCH      = "lunch",      _("Almuerzo")
        PRE_WORKOUT= "pre_workout",_("Pre-entreno")
        POST_WORKOUT="post_workout",_("Post-entreno")
        DINNER     = "dinner",     _("Cena")
        SNACK      = "snack",      _("Snack")

    plan        = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="meals")
    meal_type   = models.CharField(max_length=15, choices=MealType.choices)
    name        = models.CharField(max_length=120)
    calories    = models.PositiveIntegerField(null=True, blank=True)
    protein_g   = models.PositiveSmallIntegerField(null=True, blank=True)
    carbs_g     = models.PositiveSmallIntegerField(null=True, blank=True)
    fat_g       = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    order       = models.PositiveSmallIntegerField(default=1)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table   = "fitness_meal"
        verbose_name = "Comida"
        verbose_name_plural = "Comidas"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.meal_type} — {self.name} ({self.calories or '?'} kcal)"
