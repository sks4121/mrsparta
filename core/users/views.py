"""
core/users/views.py
───────────────────
Sistema completo de autenticación.
Soporta registro/login tradicional + Google OAuth 2.0 (allauth).
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


from .models import User
from fitness.profiles.models import ClientProfile
from coaching.coaches.models import CoachProfile






from .forms import (
    AthleteRegistrationForm,
    CoachRegistrationForm,
    LoginForm,
    PasswordResetRequestForm,
)
from .models import User


# ═══════════════════════════════════════════════════════════
#  REGISTER — Selector
# ═══════════════════════════════════════════════════════════

def register_selector(request):
    """Pantalla previa: elige si eres Atleta o Coach."""
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))
    return render(request, "auth/register_selector.html")


# ═══════════════════════════════════════════════════════════
#  REGISTER — Athlete
# ═══════════════════════════════════════════════════════════

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_athlete(request):
    if request.user.is_authenticated:
        return redirect("athlete_dashboard:athlete_dashboard")

    if request.method == "POST":
        form = AthleteRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                if _is_ajax(request):
                    return JsonResponse({
                        "success": True,
                        "redirect": reverse("athlete_dashboard:athlete_dashboard"),
                        "message": "¡Bienvenido guerrero!",
                    })
                messages.success(request, "¡Cuenta creada! Bienvenido a MR Sparta.")
                return redirect("athlete_dashboard:athlete_dashboard")

            except Exception as exc:
                error = f"Error al crear la cuenta: {exc}"
                if _is_ajax(request):
                    return JsonResponse({"success": False, "errors": {"__all__": [error]}}, status=500)
                messages.error(request, error)
        else:
            if _is_ajax(request):
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = AthleteRegistrationForm()

    return render(request, "auth/register_athlete.html", {"form": form})


# ═══════════════════════════════════════════════════════════
#  REGISTER — Coach
# ═══════════════════════════════════════════════════════════

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_coach(request):
    if request.user.is_authenticated:
        return redirect("coach_dashboard:coach_dashboard")

    if request.method == "POST":
        form = CoachRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                if _is_ajax(request):
                    return JsonResponse({
                        "success": True,
                        "redirect": reverse("coach_dashboard:coach_dashboard"),
                        "message": "¡Bienvenido Coach!",
                    })
                messages.success(request, "¡Cuenta de Coach creada!")
                return redirect("coach_dashboard:coach_dashboard")

            except Exception as exc:
                error = f"Error al crear la cuenta: {exc}"
                if _is_ajax(request):
                    return JsonResponse({"success": False, "errors": {"__all__": [error]}}, status=500)
                messages.error(request, error)
        else:
            if _is_ajax(request):
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = CoachRegistrationForm()

    return render(request, "auth/register_coach.html", {"form": form})


# ═══════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════

@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login con email + password.
    Detecta el rol del usuario y redirige a su dashboard correspondiente.
    """
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Remember me
            if not form.cleaned_data.get("remember", False):
                request.session.set_expiry(0)  # cierra al cerrar navegador
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 días

            redirect_url = next_url or _dashboard_for(user)

            if _is_ajax(request):
                return JsonResponse({
                    "success": True,
                    "redirect": redirect_url,
                    "message": f"Bienvenido {user.first_name}",
                    "role": user.role,
                })

            messages.success(request, f"Bienvenido {user.first_name} ⚔")
            return redirect(redirect_url)
        else:
            if _is_ajax(request):
                return JsonResponse({
                    "success": False,
                    "errors": form.errors,
                }, status=400)
    else:
        form = LoginForm()

    return render(request, "auth/login.html", {
        "form": form,
        "next": next_url,
    })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Cierra sesión y redirige al landing."""
    user_name = request.user.first_name if request.user.is_authenticated else ""
    logout(request)
    if user_name:
        messages.info(request, f"Sesión cerrada. Vuelve pronto, {user_name}.")
    return redirect("home")


# ═══════════════════════════════════════════════════════════
#  PASSWORD RESET REQUEST
# ═══════════════════════════════════════════════════════════

@csrf_protect
@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """Solicita link para restablecer contraseña por email."""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            form.send_reset_email(request)

            if _is_ajax(request):
                return JsonResponse({
                    "success": True,
                    "message": "Si el email existe, recibirás instrucciones en breve.",
                })

            messages.success(
                request,
                "Si el email existe, recibirás instrucciones en breve."
            )
            return redirect("users:login")
        else:
            if _is_ajax(request):
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = PasswordResetRequestForm()

    return render(request, "auth/password_reset.html", {"form": form})


# ═══════════════════════════════════════════════════════════
#  GOOGLE OAuth — wrappers
# ═══════════════════════════════════════════════════════════

def google_login(request):
    """
    Inicia el flujo OAuth con Google.
    Solo redirige al endpoint de allauth con el rol guardado en sesión.
    """
    role = request.GET.get("role", "athlete")
    if role in (User.Role.ATHLETE, User.Role.COACH):
        request.session["pending_role"] = role
    return redirect("/accounts/google/login/")


def google_callback(request):
    """
    Allauth maneja el callback automáticamente en /accounts/google/login/callback/.
    Esta vista existe solo como referencia — la lógica real está en signals.py.
    """
    return redirect("/")


def google_role_picker(request):
    """
    Pantalla post-login con Google cuando el usuario es nuevo
    y aún no tiene rol asignado. Le pide elegir entre Atleta o Coach.
    """
    if not request.user.is_authenticated:
        return redirect("users:login")

    if request.user.role and request.user.is_onboarded:
        return redirect(_dashboard_for(request.user))

    if request.method == "POST":
        role = request.POST.get("role")
        if role in (User.Role.ATHLETE, User.Role.COACH):
            request.user.role = role
            request.user.is_onboarded = True
            request.user.save(update_fields=["role", "is_onboarded"])

            # Crear el perfil correspondiente
            try:
                if role == User.Role.ATHLETE:
                    from fitness.profiles.models import ClientProfile
                    ClientProfile.objects.get_or_create(user=request.user)
                else:
                    from coaching.coaches.models import CoachProfile
                    CoachProfile.objects.get_or_create(user=request.user)
            except Exception:
                pass

            messages.success(request, "¡Bienvenido a la legión!")
            return redirect(_dashboard_for(request.user))
        messages.error(request, "Debes elegir un rol.")

    return render(request, "auth/google_role_picker.html")


# ═══════════════════════════════════════════════════════════
#  API — AJAX endpoints
# ═══════════════════════════════════════════════════════════

@require_http_methods(["POST"])
def check_email_available(request):
    """Verifica si un email está disponible (AJAX)."""
    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"available": False, "error": "Email requerido."}, status=400)

    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({
        "available": not exists,
        "message": "Email disponible" if not exists else "Este email ya está registrado.",
    })


@require_http_methods(["POST"])
def check_email_exists(request):
    """Para el login: verifica que el email SÍ exista."""
    email = (request.POST.get("email") or "").strip().lower()
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({"exists": exists})


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def _is_ajax(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _dashboard_for(user: User) -> str:
    """Resuelve URL del dashboard según el rol."""
    if user.is_coach:
        return reverse("coach_dashboard:coach_dashboard")
    if user.is_athlete:
        return reverse("athlete_dashboard:athlete_dashboard")
    return reverse("home")



@login_required
def athlete_dashboard(request):
    return render(request, "athlete_dashboard.html")

@login_required
def coach_dashboard(request):
    return render(request, "coach_dashboard.html")


@login_required
def user_profile(request):
    context = {'user': request.user}
    return render(request, 'profiles/athlete_profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        return redirect('users:user-profile')
    context = {'user': request.user}
    return render(request, 'profiles/profile_edit.html', context)

@login_required
def profile_settings(request):
    context = {'user': request.user}
    return render(request, 'profiles/profile_settings.html', context)

def athlete_profile(request, pk):
    athlete = get_object_or_404(User, pk=pk, role='athlete')
    profile = get_object_or_404(ClientProfile, user=athlete)
    context = {'user': athlete, 'profile': profile}
    return render(request, 'profiles/athlete_profile.html', context)

def coach_profile(request, pk):
    coach = get_object_or_404(User, pk=pk, role='coach')
    profile = get_object_or_404(CoachProfile, user=coach)
    context = {'coach': profile}
    return render(request, 'profiles/coach_profile.html', context)
