from django.urls import path
from . import views

app_name = 'coaches'

urlpatterns = [
    path('', views.coaches_directory, name='coaches-directory'),
    path('<int:pk>/', views.coach_detail, name='coach-detail'),
    path('profile/edit/', views.coach_profile_edit, name='coach-profile-edit'),
    path('organization/<slug:slug>/', views.organization_detail, name='organization-detail'),
]
