#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mrsparta.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except RuntimeError as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

# Ahora importar modelos
from core.users.models import User
from coaching.coaches.models import CoachProfile, Organization
from fitness.profiles.models import ClientProfile

print("="*60)
print("CREANDO DATOS DE PRUEBA")
print("="*60)

try:
    # 1. Crear usuario coach
    print("\n1. Creando usuario coach...")
    coach_user, created = User.objects.get_or_create(
        email='coach@mrsparta.com',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'role': 'coach',
            'is_active': True,
        }
    )
    if created:
        coach_user.set_password('coach123456')
        coach_user.save()
        print(f"✓ Usuario creado: {coach_user.email}")
    else:
        print(f"✓ Usuario existe: {coach_user.email}")

    # 2. Crear CoachProfile
    print("\n2. Creando perfil de coach...")
    coach_profile, created = CoachProfile.objects.get_or_create(
        user=coach_user,
        defaults={
            'specialty': 'strength',
            'bio': 'Entrenador especializado en ganancia de fuerza y musculatura.',
            'certifications': 'NASM, ISSA, CrossFit Level 2',
            'years_experience': 8,
            'session_price': 50.00,
            'session_duration': 60,
            'max_clients': 10,
            'timezone': 'America/Bogota',
            'total_clients': 3,
            'avg_compliance': 85,
            'rating': 4.8,
            'is_available': True,
            'is_verified': True,
        }
    )
    if created:
        print(f"✓ CoachProfile creado (ID: {coach_profile.pk})")
    else:
        print(f"✓ CoachProfile existe (ID: {coach_profile.pk})")

    # 3. Crear organización
    print("\n3. Creando organización...")
    org, created = Organization.objects.get_or_create(
        owner=coach_user,
        defaults={
            'name': 'MR SPARTA Strength',
            'slug': 'mr-sparta-strength',
            'description': 'Centro de entrenamiento especializado en fuerza.',
        }
    )
    if created:
        print(f"✓ Organización creada: {org.name}")
    else:
        print(f"✓ Organización existe: {org.name}")

    # 4. Crear usuario atleta
    print("\n4. Creando usuario atleta...")
    athlete_user, created = User.objects.get_or_create(
        email='athlete@mrsparta.com',
        defaults={
            'first_name': 'Carlos',
            'last_name': 'López',
            'role': 'athlete',
            'is_active': True,
        }
    )
    if created:
        athlete_user.set_password('athlete123456')
        athlete_user.save()
        print(f"✓ Usuario creado: {athlete_user.email}")
    else:
        print(f"✓ Usuario existe: {athlete_user.email}")

    # 5. Crear perfil de atleta (SIN experience_level)
    print("\n5. Creando perfil de atleta...")
    athlete_profile, created = ClientProfile.objects.get_or_create(
        user=athlete_user,
        defaults={
            'weight_kg': 75.5,
            'height_cm': 180,
            'body_fat_pct': 15.0,
            'goal': 'hypertrophy',
            # 'experience_level' NO EXISTE - removido
        }
    )
    if created:
        print(f"✓ ClientProfile creado (ID: {athlete_profile.pk})")
    else:
        print(f"✓ ClientProfile existe (ID: {athlete_profile.pk})")

    # Resumen
    print("\n" + "="*60)
    print("✅ DATOS CREADOS EXITOSAMENTE")
    print("="*60)
    print(f"\n🔐 CREDENCIALES:\n")
    print(f"COACH:")
    print(f"  Email: coach@mrsparta.com")
    print(f"  Password: coach123456")
    print(f"  CoachProfile ID: {coach_profile.pk}")
    print(f"\nATHLETE:")
    print(f"  Email: athlete@mrsparta.com")
    print(f"  Password: athlete123456")
    print(f"  ClientProfile ID: {athlete_profile.pk}")
    print(f"\n📍 URLS:\n")
    print(f"  Coach detail: http://127.0.0.1:8000/coaches/{coach_profile.pk}/")
    print(f"  Coaches dir: http://127.0.0.1:8000/coaches/")
    print(f"  Admin: http://127.0.0.1:8000/admin/")
    print("\n✓ Ahora ejecutar: python manage.py runserver")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
