"""
fitness/profiles/models.py
──────────────────────────
Perfil físico del atleta. Vinculado 1-a-1 con User.
Contiene todos los datos de evaluación inicial y objetivos.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class ClientProfile(models.Model):
    """
    Perfil físico completo del atleta.
    Se crea en el onboarding y puede actualizarse.
    """

    class Goal(models.TextChoices):
        MUSCLE_GAIN    = "muscle_gain",    _("Ganar músculo")
        FAT_LOSS       = "fat_loss",       _("Perder grasa")
        RECOMPOSITION  = "recomposition",  _("Recomposición")
        PERFORMANCE    = "performance",    _("Rendimiento")
        MAINTENANCE    = "maintenance",    _("Mantenimiento")

    class Level(models.TextChoices):
        BEGINNER     = "beginner",     _("Principiante")
        INTERMEDIATE = "intermediate", _("Intermedio")
        ADVANCED     = "advanced",     _("Avanzado")

    class ActivityLevel(models.TextChoices):
        SEDENTARY     = "sedentary",     _("Sedentario")
        LIGHT         = "light",         _("Ligero (1-2 días/sem)")
        MODERATE      = "moderate",      _("Moderado (3-4 días/sem)")
        ACTIVE        = "active",        _("Activo (5-6 días/sem)")
        VERY_ACTIVE   = "very_active",   _("Muy activo (7 días/sem)")

    # ── Relaciones ────────────────────────────────────────────
    user  = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="clients",
        limit_choices_to={"role": "coach"},
    )

    # ── Datos físicos actuales ────────────────────────────────
    weight_kg      = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm      = models.PositiveSmallIntegerField(null=True, blank=True)
    age            = models.PositiveSmallIntegerField(null=True, blank=True)
    body_fat_pct   = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    # ── Objetivos ─────────────────────────────────────────────
    goal           = models.CharField(max_length=20, choices=Goal.choices, default=Goal.MUSCLE_GAIN)
    target_weight  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    level          = models.CharField(max_length=15, choices=Level.choices, default=Level.BEGINNER)
    activity_level = models.CharField(max_length=15, choices=ActivityLevel.choices, default=ActivityLevel.MODERATE)

    # ── Información adicional ─────────────────────────────────
    injuries       = models.TextField(blank=True, default="", help_text="Lesiones o limitaciones físicas.")
    medications    = models.TextField(blank=True, default="")
    equipment      = models.TextField(blank=True, default="", help_text="Equipamiento disponible.")
    notes          = models.TextField(blank=True, default="")

    # ── Métricas calculadas (se actualizan automáticamente) ───
    bmi            = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bmr_kcal       = models.PositiveIntegerField(null=True, blank=True, help_text="Tasa metabólica basal.")
    tdee_kcal      = models.PositiveIntegerField(null=True, blank=True, help_text="Gasto calórico total diario.")

    # ── Estado ────────────────────────────────────────────────
    subscription_plan = models.CharField(max_length=10, blank=True, default="basic")
    is_active      = models.BooleanField(default=True)
    joined_at      = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    # ── Método helper ─────────────────────────────────────────
    def calculate_bmi(self) -> float | None:
        if self.weight_kg and self.height_cm:
            h = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (h * h), 1)
        return None

    def save(self, *args, **kwargs):
        self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    class Meta:
        db_table   = "fitness_clientprofile"
        verbose_name = "Perfil del Atleta"
        verbose_name_plural = "Perfiles de Atletas"
        ordering = ["-joined_at"]

    def __str__(self) -> str:
        return f"Perfil de {self.user.full_name} — {self.goal}"
