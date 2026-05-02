"""
core/users/models.py

Custom User model. Extends AbstractUser and adds role logic
for ADMIN / COACH / ATHLETE (client).

✅ SIN DUPLICACIONES - UN ÚNICO MODELO USER
✅ Compatible con django-allauth
✅ Sin errores E304

AUTH_USER_MODEL = 'users.User'   ← Configurado en settings.py
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para User.
    Permite crear usuarios con email en lugar de username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Crear usuario normal"""
        if not email:
            raise ValueError(_('El email es requerido'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crear superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Único modelo de autenticación del sistema.
    Reemplaza al User de Django por completo.
    
    ✅ Autenticación por EMAIL (no username)
    ✅ Roles: ADMIN, COACH, ATHLETE
    ✅ Compatible con django-allauth
    """

    # Eliminar el campo username predeterminado
    username = None
    
    # EMAIL como campo único principal
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('El email debe ser único')
    )

    # Configuración Django Auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Manager personalizado
    objects = CustomUserManager()

    # ─────────────────────────────────────────────────────────────
    # Roles del Sistema
    # ─────────────────────────────────────────────────────────────
    class Role(models.TextChoices):
        ADMIN   = "admin",   _("Administrador")
        COACH   = "coach",   _("Entrenador")
        ATHLETE = "athlete", _("Atleta")

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.ATHLETE,
        db_index=True,
        help_text=_("Rol del usuario en el sistema")
    )

    # ─────────────────────────────────────────────────────────────
    # Información Personal
    # ─────────────────────────────────────────────────────────────
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text=_("Número telefónico")
    )
    
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        help_text=_("Foto de perfil")
    )
    
    bio = models.TextField(
        blank=True,
        default="",
        max_length=500,
        help_text=_("Biografía corta")
    )

    # ─────────────────────────────────────────────────────────────
    # Información de Fitness
    # ─────────────────────────────────────────────────────────────
    height = models.FloatField(
        blank=True,
        null=True,
        help_text=_("Altura en cm")
    )
    
    weight = models.FloatField(
        blank=True,
        null=True,
        help_text=_("Peso en kg")
    )
    
    gender = models.CharField(
        max_length=10,
        choices=[
            ('M', _('Masculino')),
            ('F', _('Femenino')),
            ('O', _('Otro')),
        ],
        blank=True,
        null=True,
        help_text=_("Género del usuario")
    )

    # ─────────────────────────────────────────────────────────────
    # Estado de Cuenta
    # ─────────────────────────────────────────────────────────────
    is_onboarded = models.BooleanField(
        default=False,
        help_text=_("¿Completó el onboarding?")
    )
    
    is_premium = models.BooleanField(
        default=False,
        help_text=_("¿Tiene plan premium?")
    )

    # ─────────────────────────────────────────────────────────────
    # Timestamps
    # ─────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Fecha de creación de cuenta")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Última actualización")
    )

    # ─────────────────────────────────────────────────────────────
    # Propiedades Helper
    # ─────────────────────────────────────────────────────────────
    @property
    def is_coach(self) -> bool:
        """¿Es un entrenador?"""
        return self.role == self.Role.COACH

    @property
    def is_athlete(self) -> bool:
        """¿Es un atleta?"""
        return self.role == self.Role.ATHLETE

    @property
    def is_admin(self) -> bool:
        """¿Es administrador?"""
        return self.role == self.Role.ADMIN

    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        full = self.get_full_name()
        return full if full else self.email.split('@')[0]

    # ─────────────────────────────────────────────────────────────
    # Meta & String
    # ─────────────────────────────────────────────────────────────
    class Meta:
        db_table = "auth_user"
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_role_display()})"

    def get_absolute_url(self):
        """URL del perfil del usuario"""
        return f"/profile/{self.id}/"

    def save(self, *args, **kwargs):
        """Customizar guardado"""
        # Normalizar email
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)