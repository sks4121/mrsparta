"""
fitness/plans/views.py
──────────────────────
Vistas profesionales para la app de planes de fitness.

Incluye:
    • Class-Based Views (TemplateView / DetailView / ListView) para HTML
    • API JSON con LoginRequired + manejo de errores robusto
    • Logging estructurado
    • Validación de permisos (cada usuario sólo ve sus propios planes)
"""
from __future__ import annotations

import logging
from typing import Any
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView, TemplateView

from ai.engine.services import generate_plan
from fitness.profiles.models import ClientProfile as Profile
from .models import Plan, TrainingDay, Exercise, Meal

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
#  MIXINS
# ════════════════════════════════════════════════════════════════
class OwnerQuerysetMixin:
    """Filtra el queryset para que el usuario sólo vea sus propios planes."""

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()  # type: ignore[misc]
        return qs.filter(client=self.request.user)  # type: ignore[attr-defined]


# ════════════════════════════════════════════════════════════════
#  VISTAS HTML
# ════════════════════════════════════════════════════════════════
class PlanListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    """Lista de planes del usuario autenticado."""

    model = Plan
    template_name = "plans/plan_list.html"
    context_object_name = "plans"
    paginate_by = 10


class PlanDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    """Detalle de un plan específico (con sus días, ejercicios y comidas)."""

    model = Plan
    template_name = "plans/plan_detail.html"
    context_object_name = "plan"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        plan: Plan = ctx["plan"]
        ctx["training_days"] = plan.training_days.prefetch_related("exercises").all()
        ctx["meals"] = plan.meals.all()
        return ctx


class _TierBaseView(LoginRequiredMixin, TemplateView):
    """Base para las páginas de tier (basic/premium/elite)."""

    tier: str = ""
    tier_label: str = ""
    price_monthly: int = 0
    features: list[str] = []

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            tier=self.tier,
            tier_label=self.tier_label,
            price_monthly=self.price_monthly,
            features=self.features,
            current_plan=Plan.objects.filter(
                client=self.request.user,
                status=Plan.Status.ACTIVE,
            ).first(),
        )
        return ctx


class PlanBasicView(_TierBaseView):
    template_name = "plans/planbasic.html"
    tier = "basic"
    tier_label = "Basic"
    price_monthly = 0
    features = [
        "1 plan de entrenamiento por mes",
        "Plan nutricional general",
        "Seguimiento básico de ejercicios",
        "Acceso a la app móvil",
    ]


class PlanPremiumView(_TierBaseView):
    template_name = "plans/planpremium.html"
    tier = "premium"
    tier_label = "Premium"
    price_monthly = 29
    features = [
        "Planes ilimitados generados por IA",
        "Macros personalizados (proteína, carbos, grasa)",
        "Tracking avanzado con gráficos",
        "Videos demostrativos de ejercicios",
        "Reportes semanales de progreso",
        "Soporte por email 24/7",
    ]


class PlanEliteView(_TierBaseView):
    template_name = "plans/planelite.html"
    tier = "elite"
    tier_label = "Elite"
    price_monthly = 99
    features = [
        "Todo lo de Premium",
        "Coach humano asignado",
        "Plan ajustado semanalmente por tu coach",
        "Videollamadas mensuales",
        "Análisis biométrico avanzado",
        "Plan de suplementación personalizado",
        "Acceso prioritario a nuevas funciones",
        "Soporte VIP por WhatsApp",
    ]


# ════════════════════════════════════════════════════════════════
#  API JSON
# ════════════════════════════════════════════════════════════════
@method_decorator(csrf_protect, name="dispatch")
class PlanCreateAPIView(LoginRequiredMixin, View):
    """
    POST /plans/api/create/
    Genera un plan nuevo usando el motor de IA a partir del perfil del usuario.
    """

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            logger.warning("Plan creation aborted: user %s has no profile", request.user.id)
            return JsonResponse(
                {"error": "Debes completar tu perfil antes de generar un plan."},
                status=400,
            )

        try:
            data = generate_plan(profile)
        except Exception as exc:  # noqa: BLE001 – logueamos cualquier fallo del motor de IA
            logger.exception("AI engine failed for user %s: %s", request.user.id, exc)
            return JsonResponse(
                {"error": "El motor de IA no pudo generar el plan. Inténtalo de nuevo."},
                status=503,
            )

        logger.info("Plan generated successfully for user %s", request.user.id)
        return JsonResponse({"ok": True, "plan": data}, status=201)


class PlanDetailAPIView(LoginRequiredMixin, View):
    """GET /plans/api/<id>/ → Devuelve un plan en formato JSON."""

    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        plan = get_object_or_404(Plan, pk=pk, client=request.user)

        payload = {
            "id": plan.id,
            "name": plan.name,
            "type": plan.plan_type,
            "status": plan.status,
            "week": f"{plan.week_number}/{plan.total_weeks}",
            "macros": {
                "calories": plan.daily_calories,
                "protein_g": plan.protein_g,
                "carbs_g": plan.carbs_g,
                "fat_g": plan.fat_g,
                "water_l": float(plan.water_liters) if plan.water_liters else None,
            },
            "training_days": [
                {
                    "id": d.id,
                    "day": d.day_name,
                    "focus": d.focus,
                    "is_rest": d.is_rest_day,
                    "exercises": [
                        {
                            "id": e.id,
                            "name": e.name,
                            "sets": e.sets,
                            "reps": e.reps,
                            "weight_kg": float(e.weight_kg) if e.weight_kg else None,
                            "rest_seconds": e.rest_seconds,
                            "rpe": e.rpe,
                            "video_url": e.video_url,
                            "completed": e.is_completed,
                        }
                        for e in d.exercises.all()
                    ],
                }
                for d in plan.training_days.prefetch_related("exercises")
            ],
            "meals": [
                {
                    "id": m.id,
                    "type": m.meal_type,
                    "name": m.name,
                    "calories": m.calories,
                    "protein_g": m.protein_g,
                    "carbs_g": m.carbs_g,
                    "fat_g": m.fat_g,
                    "completed": m.is_completed,
                }
                for m in plan.meals.all()
            ],
        }
        return JsonResponse(payload)


@method_decorator(csrf_protect, name="dispatch")
class ExerciseCompleteAPIView(LoginRequiredMixin, View):
    """POST /plans/api/exercise/<id>/done/ → Marca un ejercicio como completado."""

    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        exercise = get_object_or_404(
            Exercise.objects.select_related("training_day__plan"),
            pk=pk,
            training_day__plan__client=request.user,
        )
        exercise.is_completed = not exercise.is_completed
        exercise.save(update_fields=["is_completed"])
        return JsonResponse({"ok": True, "completed": exercise.is_completed})


@method_decorator(csrf_protect, name="dispatch")
class MealCompleteAPIView(LoginRequiredMixin, View):
    """POST /plans/api/meal/<id>/done/ → Marca una comida como consumida."""

    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        meal = get_object_or_404(Meal, pk=pk, plan__client=request.user)
        meal.is_completed = not meal.is_completed
        meal.save(update_fields=["is_completed"])
        return JsonResponse({"ok": True, "completed": meal.is_completed})








@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    context = {'plan': plan}
    return render(request, 'fitness/plan_detail.html', context)

@login_required
def plan_week(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    training_days = plan.trainingday_set.all()
    context = {'plan': plan, 'training_days': training_days, 'week_number': 1}
    return render(request, 'fitness/plan_week.html', context)

@login_required
def training_day_detail(request, pk):
    training_day = get_object_or_404(TrainingDay, pk=pk)
    context = {'training_day': training_day}
    return render(request, 'fitness/training_day.html', context)

@login_required
def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    context = {'exercise': exercise}
    return render(request, 'fitness/exercise_detail.html', context)

@login_required
def meal_plan(request):
    meals = Meal.objects.all()
    context = {'meals': meals}
    return render(request, 'fitness/meal_plan.html', context)
