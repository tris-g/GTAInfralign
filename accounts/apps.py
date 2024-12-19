from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Creates a default superuser if one is not active.
        from .signals import initialise_superuser
        post_migrate.connect(initialise_superuser, sender=self)