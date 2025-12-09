from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = "Codeteki Content"

    def ready(self):
        """Import signals to register them when Django starts."""
        import core.signals  # noqa: F401
