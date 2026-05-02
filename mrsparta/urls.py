from django.contrib import admin
from django.urls import path, include
from mrsparta.views import index, schema
from django.conf.urls.static import static
from django.conf import settings
from . import views

from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', index, name='home'),
    
    # ✅ CAMBIAR: login namespace
    path('login/', include(('core.users.urls', 'login'), namespace='users_login')),
    
    # ✅ CAMBIAR: athlete_dashboard namespace
    path('athlete_dashboard/', include(('core.users.urls', 'athlete_dashboard'), namespace='athlete_dashboard')),
    
    # ✅ CAMBIAR: coach_dashboard namespace
    path('coach_dashboard/', include(('core.users.urls', 'coach_dashboard'), namespace='coach_dashboard')),

    # ✅ CAMBIAR: register_athlete namespace (NO 'accounts')
    path('register_athlete/', include(('core.users.urls', 'register_athlete'), namespace='users_register')),

    # ✅ SOLO ALLAUTH CON accounts
    path('accounts/', include('allauth.urls')),
    
    # ✅ Plans
    path('plans/', include('fitness.plans.urls')),

    path('schema', schema, name='schema'),


    # Usuarios y Autenticación
    path('users/', include('core.users.urls')),
    
    # Perfiles y Configuración
    path('profile/', include('core.users.urls')),
    
    # Fitness y Planes
    
    path('progress/', include('fitness.progress.urls')),
    path('photos/', include('fitness.photos.urls')),
    path('profiles/', include('fitness.profiles.urls')),
    
    # Coaching y Sesiones
    path('coaches/', include('coaching.coaches.urls')),
    path('sessions/', include('coaching.coach_sessions.urls')),
    
    # Billing y Pagos
    path('billing/', include('core.billing.urls')),
    
    # Páginas estáticas
    #path('pages/', include('pages_urls')),
    
    # API (futuro)
    # path('api/', include('api.urls')),

     
    # Marketing Pages - Usando vistas
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy_policy, name='privacy-policy'),
    path('terms/', views.terms_conditions, name='terms-conditions'),
    path('notifications/', views.notifications, name='notifications'),
]
# Debug
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)