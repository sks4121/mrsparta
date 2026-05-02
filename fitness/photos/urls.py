from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.photo_list, name='photo-list'),
    path('<int:pk>/', views.photo_detail, name='photo-detail'),
    path('upload/', views.photo_upload, name='photo-upload'),
    path('<int:pk>/delete/', views.photo_delete, name='photo-delete'),
]
