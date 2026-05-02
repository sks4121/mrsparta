"""
fitness/plans/urls.py
─────────────────────
Rutas de la aplicación de planes de entrenamiento y nutrición.

Estructura:
    /plans/                    → Lista de planes del usuario
    /plans/basic/              → Vista del plan tier Basic
    /plans/premium/            → Vista del plan tier Premium
    /plans/elite/              → Vista del plan tier Elite
    /plans/<id>/               → Detalle de un plan específico
    /plans/api/create/         → Generar plan con IA (POST)
    /plans/api/<id>/           → API de un plan
    /plans/api/exercise/<id>/  → Marcar ejercicio como completado
    /plans/api/meal/<id>/      → Marcar comida como completada
"""
from django.urls import path

from . import views

app_name = "plans"

urlpatterns = [
    # ── Vistas HTML (templates) ──────────────────────────────
    path("",                      views.PlanListView.as_view(),    name="list"),
    path("basic/",                views.PlanBasicView.as_view(),   name="basic"),
    path("premium/",              views.PlanPremiumView.as_view(), name="premium"),
    path("elite/",                views.PlanEliteView.as_view(),   name="elite"),
    path("<int:pk>/",             views.PlanDetailView.as_view(),  name="detail"),

    # ── API REST (JSON) ──────────────────────────────────────
    path("api/create/",                 views.PlanCreateAPIView.as_view(),     name="api-create"),
    path("api/<int:pk>/",               views.PlanDetailAPIView.as_view(),     name="api-detail"),
    path("api/exercise/<int:pk>/done/", views.ExerciseCompleteAPIView.as_view(), name="api-exercise-done"),
    path("api/meal/<int:pk>/done/",     views.MealCompleteAPIView.as_view(),    name="api-meal-done"),


    path('<int:pk>/', views.plan_detail, name='plan-detail'),
    path('<int:pk>/week/', views.plan_week, name='plan-week'),
    path('training-day/<int:pk>/', views.training_day_detail, name='training-day'),
    path('exercise/<int:pk>/', views.exercise_detail, name='exercise-detail'),
    path('meal-plan/', views.meal_plan, name='meal-plan'),
]
