"""
core/users/forms.py
───────────────────
Formularios completos de autenticación.
"""
from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User


# ═══════════════════════════════════════════════════════════
#  BASE — Common fields
# ═══════════════════════════════════════════════════════════

class BaseRegistrationForm(forms.Form):
    """Base con campos comunes a Atleta y Coach."""

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "Juan",
            "autocomplete": "given-name",
        }),
        error_messages={"required": "El nombre es obligatorio."},
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "Martínez",
            "autocomplete": "family-name",
        }),
        error_messages={"required": "El apellido es obligatorio."},
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "tu@email.com",
            "autocomplete": "email",
        }),
        error_messages={
            "required": "El email es obligatorio.",
            "invalid":  "Ingresa un email válido.",
        },
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Mínimo 8 caracteres",
            "autocomplete": "new-password",
        }),
        error_messages={"required": "La contraseña es obligatoria."},
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repite la contraseña",
            "autocomplete": "new-password",
        }),
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={"required": "Debes aceptar los términos y condiciones."},
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1", "")
        password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned


# ═══════════════════════════════════════════════════════════
#  ATHLETE
# ═══════════════════════════════════════════════════════════

class AthleteRegistrationForm(BaseRegistrationForm):
    GOAL_CHOICES = [
        ("muscle_gain",   "Ganar músculo"),
        ("fat_loss",      "Perder grasa"),
        ("recomposition", "Recomposición"),
        ("performance",   "Rendimiento"),
        ("maintenance",   "Mantenimiento"),
    ]
    LEVEL_CHOICES = [
        ("beginner",     "Principiante"),
        ("intermediate", "Intermedio"),
        ("advanced",     "Avanzado"),
    ]

    age = forms.IntegerField(
        min_value=13, max_value=100,
        widget=forms.NumberInput(attrs={"placeholder": "25"}),
        error_messages={
            "required": "La edad es obligatoria.",
            "min_value": "Debes tener al menos 13 años.",
            "max_value": "Edad inválida.",
        },
    )
    weight_kg = forms.DecimalField(
        min_value=30, max_value=300, decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "75.5", "step": "0.1"}),
        error_messages={"required": "El peso es obligatorio."},
    )
    height_cm = forms.IntegerField(
        min_value=100, max_value=250,
        widget=forms.NumberInput(attrs={"placeholder": "178"}),
        error_messages={"required": "La altura es obligatoria."},
    )
    goal = forms.ChoiceField(
        choices=GOAL_CHOICES,
        error_messages={"required": "Selecciona tu objetivo."},
    )
    level = forms.ChoiceField(choices=LEVEL_CHOICES, initial="beginner")

    @transaction.atomic
    def save(self) -> User:
        from fitness.profiles.models import ClientProfile

        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password1"],
            role=User.Role.ATHLETE,
            is_onboarded=True,
        )
        ClientProfile.objects.create(
            user=user,
            age=data["age"],
            weight_kg=data["weight_kg"],
            height_cm=data["height_cm"],
            goal=data["goal"],
            level=data["level"],
        )
        return user


# ═══════════════════════════════════════════════════════════
#  COACH
# ═══════════════════════════════════════════════════════════

class CoachRegistrationForm(BaseRegistrationForm):
    SPECIALTY_CHOICES = [
        ("strength",     "Fuerza"),
        ("hypertrophy",  "Hipertrofia"),
        ("fat_loss",     "Pérdida de grasa"),
        ("powerlifting", "Powerlifting"),
        ("crossfit",     "CrossFit"),
        ("nutrition",    "Nutrición deportiva"),
        ("general",      "Fitness general"),
    ]

    specialty = forms.ChoiceField(
        choices=SPECIALTY_CHOICES,
        error_messages={"required": "Selecciona una especialidad."},
    )
    years_experience = forms.IntegerField(
        min_value=0, max_value=70,
        widget=forms.NumberInput(attrs={"placeholder": "5"}),
        error_messages={"required": "Los años de experiencia son obligatorios."},
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Cuéntanos sobre ti (opcional)"}),
        required=False, max_length=500,
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={"placeholder": "+57 300 000 0000", "autocomplete": "tel"}),
    )

    @transaction.atomic
    def save(self) -> User:
        from coaching.coaches.models import CoachProfile

        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password1"],
            role=User.Role.COACH,
            phone=data.get("phone", ""),
            is_onboarded=True,
        )
        CoachProfile.objects.create(
            user=user,
            specialty=data["specialty"],
            years_experience=data["years_experience"],
            bio=data.get("bio", ""),
        )
        return user


# ═══════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════

class LoginForm(forms.Form):
    """Login con email + password + remember."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "tu@email.com",
            "autocomplete": "email",
        }),
        error_messages={
            "required": "El email es obligatorio.",
            "invalid":  "Ingresa un email válido.",
        },
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Tu contraseña",
            "autocomplete": "current-password",
        }),
        error_messages={"required": "La contraseña es obligatoria."},
    )
    remember = forms.BooleanField(required=False)

    _user_cache = None

    def clean(self):
        cleaned = super().clean()
        email    = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password", "")

        if email and password:
            self._user_cache = authenticate(username=email, password=password)
            if self._user_cache is None:
                raise ValidationError("Email o contraseña incorrectos.")
            if not self._user_cache.is_active:
                raise ValidationError("Esta cuenta está desactivada.")
        return cleaned

    def get_user(self) -> User | None:
        return self._user_cache


# ═══════════════════════════════════════════════════════════
#  PASSWORD RESET
# ═══════════════════════════════════════════════════════════

class PasswordResetRequestForm(forms.Form):
    """Solicita reset de contraseña por email."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "tu@email.com",
            "autocomplete": "email",
        }),
        error_messages={
            "required": "El email es obligatorio.",
            "invalid":  "Ingresa un email válido.",
        },
    )

    def send_reset_email(self, request):
        """
        Envía email con link de reset.
        Por seguridad, NO informa si el email existe o no.
        """
        email = self.cleaned_data["email"].strip().lower()
        users = User.objects.filter(email__iexact=email, is_active=True)

        for user in users:
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = reverse("users:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            reset_url  = request.build_absolute_uri(reset_path)

            subject = "MR Sparta — Restablece tu contraseña"
            body = (
                f"Hola {user.first_name},\n\n"
                f"Recibimos una solicitud para restablecer tu contraseña.\n"
                f"Haz clic en el siguiente enlace (válido por 24 horas):\n\n"
                f"{reset_url}\n\n"
                f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
                f"⚔ El equipo de MR Sparta"
            )
            try:
                send_mail(
                    subject, body,
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
