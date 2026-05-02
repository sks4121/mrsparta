"""
core/users/apps.py
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.users"
    verbose_name = "Usuarios"

    def ready(self):
        """Importa los signals al iniciar Django."""
        from . import signals  # noqa
