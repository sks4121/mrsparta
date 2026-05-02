"""
Django settings for mrsparta project.
Production-ready configuration with django-allauth (NEW FORMAT - No deprecations)
"""

from pathlib import Path
import environ 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# Environment Variables
# ─────────────────────────────────────────────────────────────────────────────
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ─────────────────────────────────────────────────────────────────────────────
# Security Settings
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY = 'django-insecure-yxkrno$fq1@)*6z53&jwvxo7*jbt#)vgeiab5=sxn$44p0y84%'
DEBUG = True
ALLOWED_HOSTS = []

# ─────────────────────────────────────────────────────────────────────────────
# § 1. INSTALLED APPS
# ─────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django Built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # ← REQUIRED for django-allauth

    # Django-allauth (OAuth2, Email Auth)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # MR SPARTA Core
    'core.users.apps.UsersConfig',
    'core.billing',

    # MR SPARTA Fitness
    'fitness.profiles',
    'fitness.plans',
    'fitness.progress',
    'fitness.photos',

    # MR SPARTA AI
    'ai.engine',
    'ai.rules',
    'ai.insights',

    # MR SPARTA Coaching
    'coaching.coaches',
    'coaching.coach_sessions',

    # MR SPARTA Engagement
    'engagement.chat',
    'engagement.notifications',


]

# ─────────────────────────────────────────────────────────────────────────────
# § 2. MIDDLEWARE
# ─────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # ← For allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─────────────────────────────────────────────────────────────────────────────
# § 3. URLS & TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────
ROOT_URLCONF = 'mrsparta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'mrsparta.wsgi.application'

# ─────────────────────────────────────────────────────────────────────────────
# § 4. DATABASE
# ─────────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# § 5. AUTHENTICATION & USER
# ─────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ─────────────────────────────────────────────────────────────────────────────
# § 6. DJANGO-ALLAUTH CONFIGURATION (NEW FORMAT - NO DEPRECATIONS ✅)
# ─────────────────────────────────────────────────────────────────────────────

SITE_ID = 1  # ← REQUIRED for allauth

# Login & Logout Redirects
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Authentication Method (NEW FORMAT)
ACCOUNT_LOGIN_METHODS = {
    'email': True,
}

# Signup Fields (NEW FORMAT)
ACCOUNT_SIGNUP_FIELDS = [
    'email*',
    'password1*',
    'password2*',
]

# Email Configuration
#ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
#ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'mandatory' in production
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# Social Account Auto-Signup
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# ─────────────────────────────────────────────────────────────────────────────
# § 7. GOOGLE OAUTH2 CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID'),
            'secret': env('GOOGLE_CLIENT_SECRET'),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# § 8. EMAIL BACKEND
# ─────────────────────────────────────────────────────────────────────────────

# Development (Console - prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production (Uncomment and configure)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'MR Sparta <noreply@mrsparta.com>'

# ─────────────────────────────────────────────────────────────────────────────
# § 9. INTERNATIONALIZATION
# ─────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────────────────────
# § 10. STATIC & MEDIA FILES
# ─────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────────────────────────────────────────
# § 11. DJANGO DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#APPEND_SLASH = True
APPEND_SLASH = False




# ═════════════════════════════════════════════════════════════════════════════
# END OF SETTINGS
# ═════════════════════════════════════════════════════════════════════════════