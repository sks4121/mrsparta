"""
fitness/photos/models.py
────────────────────────
Fotos de progreso del atleta.
Se almacenan en AWS S3 (o local en dev).
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgressPhoto(models.Model):
    """
    Foto de progreso vinculada a un atleta y semana.
    """

    class Angle(models.TextChoices):
        FRONT   = "front",   _("Frente")
        BACK    = "back",    _("Espalda")
        SIDE_L  = "side_l",  _("Perfil izquierdo")
        SIDE_R  = "side_r",  _("Perfil derecho")
        OTHER   = "other",   _("Otro")

    # ── Relaciones ────────────────────────────────────────────
    client      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photos",
        limit_choices_to={"role": "athlete"},
    )
    progress_log = models.ForeignKey(
        "progress.ProgressLog",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="photos",
    )

    # ── Imagen ────────────────────────────────────────────────
    image       = models.ImageField(
        upload_to="progress_photos/%Y/%m/",
        help_text="Almacenada en S3 en producción.",
    )
    image_url   = models.URLField(
        blank=True, default="",
        help_text="URL pública de S3 (se rellena automáticamente).",
    )
    thumbnail_url = models.URLField(blank=True, default="")

    # ── Metadatos ─────────────────────────────────────────────
    angle       = models.CharField(max_length=8, choices=Angle.choices, default=Angle.FRONT)
    week_number = models.PositiveSmallIntegerField(default=1)
    taken_at    = models.DateField(null=True, blank=True)
    notes       = models.TextField(blank=True, default="")

    # ── Visibilidad ───────────────────────────────────────────
    visible_to_coach = models.BooleanField(default=True)
    is_comparison    = models.BooleanField(
        default=False,
        help_text="True si el coach la marcó como foto de comparación.",
    )
    uploaded_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table   = "fitness_progressphoto"
        verbose_name = "Foto de Progreso"
        verbose_name_plural = "Fotos de Progreso"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["client", "week_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.client.full_name} — Semana {self.week_number} ({self.angle})"

    def save(self, *args, **kwargs):
        """Auto-completa image_url desde el campo image si está vacío."""
        super().save(*args, **kwargs)
        if self.image and not self.image_url:
            self.image_url = self.image.url
            ProgressPhoto.objects.filter(pk=self.pk).update(image_url=self.image_url)
