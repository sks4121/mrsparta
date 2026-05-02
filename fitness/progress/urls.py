from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('tracker/', views.progress_tracker, name='progress-tracker'),
    path('log/create/', views.progress_log_create, name='progress-log-create'),
    path('log/<int:pk>/', views.progress_log_detail, name='progress-log-detail'),
    path('sessions/', views.workout_session_list, name='workout-sessions'),
    path('session/<int:pk>/', views.workout_session_detail, name='workout-session-detail'),
]
