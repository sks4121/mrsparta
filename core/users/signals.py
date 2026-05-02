"""
core/users/signals.py
─────────────────────
Signals para manejar eventos de autenticación con allauth.
Cuando un usuario se registra por Google, lo enviamos al
selector de rol antes de acceder al dashboard.
"""
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

from .models import User


@receiver(user_signed_up)
def on_user_signed_up(sender, request, user, **kwargs):
    """
    Se dispara cuando un usuario se registra por allauth (Google).
    
    Si viene de Google, marcamos is_onboarded=False para forzar
    al selector de rol después del callback.
    """
    socialaccount = kwargs.get("sociallogin")
    if socialaccount and socialaccount.account.provider == "google":
        # El rol se asignará en /auth/google/role/
        user.is_onboarded = False

        # Si la sesión tiene un rol pendiente (del query param), úsalo
        pending_role = request.session.pop("pending_role", None) if request else None
        if pending_role in (User.Role.ATHLETE, User.Role.COACH):
            user.role = pending_role
            user.is_onboarded = True

            # Crear perfil correspondiente
            try:
                if pending_role == User.Role.ATHLETE:
                    from fitness.profiles.models import ClientProfile
                    ClientProfile.objects.get_or_create(user=user)
                else:
                    from coaching.coaches.models import CoachProfile
                    CoachProfile.objects.get_or_create(user=user)
            except Exception:
                pass

        user.save(update_fields=["is_onboarded", "role"])


@receiver(social_account_added)
def on_social_account_added(sender, request, sociallogin, **kwargs):
    """Cuando se vincula una cuenta de Google a un usuario existente."""
    pass
