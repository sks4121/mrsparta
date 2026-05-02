"""
coaching/coaches/models.py
──────────────────────────
Perfil profesional de coaches y organizaciones.
Datos públicos, especialidades, certificaciones.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CoachProfile(models.Model):
    """
    Perfil profesional del Coach.
    Extiende User con información pública y de negocio.
    """

    class Specialty(models.TextChoices):
        STRENGTH = "strength", _("Fuerza")
        HYPERTROPHY = "hypertrophy", _("Hipertrofia")
        FAT_LOSS = "fat_loss", _("Pérdida de grasa")
        POWERLIFTING = "powerlifting", _("Powerlifting")
        CROSSFIT = "crossfit", _("CrossFit")
        NUTRITION = "nutrition", _("Nutrición deportiva")
        GENERAL = "general", _("Fitness general")

    # ── Relación ──────────────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coach_profile",
        limit_choices_to={"role": "coach"},
    )

    # ── Info pública ──────────────────────────────────────────
    bio = models.TextField(
        blank=True,
        default="",
        help_text=_("Biografía del coach"),
    )
    specialty = models.CharField(
        max_length=15,
        choices=Specialty.choices,
        default=Specialty.GENERAL,
        help_text=_("Especialidad principal"),
    )
    certifications = models.TextField(
        blank=True,
        default="",
        help_text=_("Certificaciones y credenciales (separadas por comas)"),
    )
    years_experience = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Años de experiencia"),
    )
    instagram_url = models.URLField(
        blank=True,
        default="",
        help_text=_("URL de Instagram"),
    )
    website_url = models.URLField(
        blank=True,
        default="",
        help_text=_("URL de sitio web personal"),
    )

    # ── Configuración del negocio ─────────────────────────────
    session_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_("Precio por sesión de coaching"),
    )
    session_duration = models.PositiveSmallIntegerField(
        default=60,
        help_text=_("Duración estándar de sesión en minutos"),
    )
    max_clients = models.PositiveSmallIntegerField(
        default=20,
        help_text=_("Máximo de clientes simultáneos"),
    )
    timezone = models.CharField(
        max_length=50,
        default="America/Bogota",
        help_text=_("Zona horaria del coach"),
    )

    # ── Métricas ──────────────────────────────────────────────
    total_clients = models.PositiveIntegerField(
        default=0,
        help_text=_("Total de clientes que ha tenido"),
    )
    avg_compliance = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text=_("Cumplimiento promedio de sus clientes (%)"),
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        help_text=_("Rating de 0 a 5"),
    )
    is_available = models.BooleanField(
        default=True,
        help_text=_("¿Está disponible para nuevos clientes?"),
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("¿Ha sido verificado por administración?"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Fecha de creación del perfil"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Fecha de última actualización"),
    )

    class Meta:
        db_table = "coaching_coachprofile"
        verbose_name = _("Perfil del Coach")
        verbose_name_plural = _("Perfiles de Coaches")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["specialty"]),
            models.Index(fields=["is_available"]),
        ]

    def __str__(self) -> str:
        return f"Coach {self.user.full_name} — {self.get_specialty_display()}"

    @property
    def active_clients_count(self) -> int:
        """Contar clientes activos (que tienen sesiones próximas)"""
        from django.utils import timezone
        from coaching.coach_sessions.models import CoachSession

        return (
            CoachSession.objects.filter(
                coach=self.user,
                status="scheduled",
                scheduled_at__gt=timezone.now(),
            )
            .values("client")
            .distinct()
            .count()
        )

    def can_accept_new_client(self) -> bool:
        """¿Puede aceptar nuevo cliente?"""
        return self.active_clients_count < self.max_clients


class Organization(models.Model):
    """
    Organización / marca del coach.
    Multi-tenant: cada coach tiene su propio espacio.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization",
        limit_choices_to={"role": "coach"},
    )
    name = models.CharField(
        max_length=120,
        help_text=_("Nombre de la organización"),
    )
    slug = models.SlugField(
        unique=True,
        help_text=_("Identificador único de la organización (URL-friendly)"),
    )
    logo = models.ImageField(
        upload_to="org_logos/",
        null=True,
        blank=True,
        help_text=_("Logo de la organización"),
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text=_("Descripción de la organización"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Fecha de creación"),
    )

    class Meta:
        db_table = "coaching_organization"
        verbose_name = _("Organización")
        verbose_name_plural = _("Organizaciones")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner.full_name})"

    def get_absolute_url(self) -> str:
        """URL de la organización"""
        return f"/coach/{self.slug}/"