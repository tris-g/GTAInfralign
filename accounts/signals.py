import os, logging
from django.contrib.auth.models import User

logger = logging.getLogger()

def initialise_superuser(sender, **kwargs):
    if not User.objects.filter(is_superuser=True).exists():
        logger.warning('No default superuser found, creating one...')
        User.objects.create_superuser(
            username='admin',
            password=os.getenv('DJANGO_SUPERUSER_PASSWORD')
        )
        logger.info('Default superuser created.')