from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.client_profile, name='client-profile'),
    path('edit/', views.client_profile_edit, name='client-profile-edit'),
]
