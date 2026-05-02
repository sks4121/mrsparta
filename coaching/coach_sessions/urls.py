from django.urls import path
from . import views

app_name = 'coach_sessions'

urlpatterns = [
    path('', views.session_list, name='session-list'),
    path('booking/<int:coach_id>/', views.session_booking, name='session-booking'),
    path('<int:pk>/', views.session_detail, name='session-detail'),
    path('<int:pk>/video/', views.session_video, name='session-video'),
    path('<int:pk>/complete/', views.session_complete, name='session-complete'),
    path('<int:pk>/cancel/', views.session_cancel, name='session-cancel'),
]
