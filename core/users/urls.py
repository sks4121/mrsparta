"""
core/users/urls.py
──────────────────
Rutas REST-friendly para todo el sistema de autenticación.
"""
from django.urls import path

from . import views


app_name = "users"

urlpatterns = [

    # ── REGISTER ───────────────────────────────────────────
    path("register/",         views.register_selector, name="register"),
    path("register/athlete/", views.register_athlete,  name="register_athlete"),
    path("register/coach/",   views.register_coach,    name="register_coach"),

    # ── LOGIN / LOGOUT ─────────────────────────────────────
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ── PASSWORD RESET ─────────────────────────────────────
    path(
        "password-reset/",
        views.password_reset_request,
        name="password_reset",
    ),

    # ── GOOGLE OAuth ───────────────────────────────────────
    path("login/google/",         views.google_login,       name="google_login"),
    path("auth/google/callback/", views.google_callback,    name="google_callback"),
    path("auth/google/role/",     views.google_role_picker, name="google_role_picker"),

    # ── API (AJAX) ─────────────────────────────────────────
    path("api/check-email/",       views.check_email_available, name="api_check_email"),
    path("api/check-email-exists/", views.check_email_exists,    name="api_check_exists"),



    path("athlete_dashboard/", views.athlete_dashboard, name="athlete_dashboard"),
    path("coach_dashboard/", views.coach_dashboard, name="coach_dashboard"),

    path('profile/', views.user_profile, name='user-profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('profile/settings/', views.profile_settings, name='profile-settings'),
    path('athlete/profile/<int:pk>/', views.athlete_profile, name='athlete-profile'),
    path('coach/profile/<int:pk>/', views.coach_profile, name='coach-profile'),
]
